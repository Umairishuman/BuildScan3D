package com.buildscan3d.app;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.util.Locale;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;
import org.json.JSONArray;
import org.json.JSONObject;

public class ProcessingActivity extends AppCompatActivity {
    private static final String TAG = "ProcessingActivity";
    static final String PREF_SERVER_URL = "server_url";
    static final String DEFAULT_SERVER_URL = "http://192.168.1.100:8000";

    private ProgressBar progressBar;
    private TextView tvStatus;
    private TextView tvStep;
    private TextView tvElapsed;
    private TextView tvLogs;
    private Button btnRetry;
    private Button btnBack;

    private String datasetPath;
    private String jobId;
    private String serverUrl;
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)   // a dropped link fails in 30 s
            .readTimeout(120, java.util.concurrent.TimeUnit.SECONDS)  // the server saves the files before answering
            .build();
    private boolean polling = false;
    // Stop button: the running upload request, and whether the user asked to stop it
    private volatile okhttp3.Call uploadCall;
    private volatile boolean uploading = false;
    private volatile boolean stopRequested = false;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_processing);

        progressBar = findViewById(R.id.progress_bar);
        tvStatus = findViewById(R.id.tv_status);
        tvStep = findViewById(R.id.tv_step);
        tvElapsed = findViewById(R.id.tv_elapsed);
        tvLogs = findViewById(R.id.tv_logs);
        btnRetry = findViewById(R.id.btn_retry);
        btnBack = findViewById(R.id.btn_back_processing);

        btnBack.setOnClickListener(v -> {
            if (uploading) {
                stopUpload();
            } else {
                finish();
            }
        });
        btnRetry.setOnClickListener(v -> {
            btnRetry.setVisibility(View.GONE);
            checkThenUpload();
        });

        serverUrl = PreferenceManager.getDefaultSharedPreferences(this)
                .getString(PREF_SERVER_URL, DEFAULT_SERVER_URL);

        datasetPath = getIntent().getStringExtra("dataset_path");
        if (datasetPath == null || datasetPath.isEmpty()) {
            tvStatus.setText("Error: No dataset path provided");
            return;
        }

        checkThenUpload();
    }

    /**
     * Checks before anything is sent: the recording has the files the server needs, then the connection. No server ->
     * asks to connect the USB cable or the Wi-Fi; Wi-Fi only -> offers the faster USB cable first; USB -> uploads.
     */
    private void checkThenUpload() {
        File dir = new File(datasetPath);
        StringBuilder missing = new StringBuilder();
        for (String name : new String[] {"dataset.mp4", "poses.csv", "tracking.csv", "points.csv", "quality.csv",
                "meta.json"}) {
            File f = new File(dir, name);
            if (!f.isFile() || f.length() == 0) missing.append(missing.length() > 0 ? ", " : "").append(name);
        }
        if (missing.length() > 0) {
            tvStatus.setText("Recording incomplete");
            tvStep.setText("Missing or empty: " + missing + ". Record the scan again.");
            return;
        }
        tvStatus.setText("Checking the connection...");
        tvStep.setText("USB cable first, then Wi-Fi");
        progressBar.setIndeterminate(true);
        new Thread(() -> {
            ServerLink.State st = ServerLink.resolve(this);
            runOnUiThread(() -> {
                if (isFinishing()) return;
                progressBar.setIndeterminate(false);
                if (st.route == ServerLink.Route.USB) {
                    startUpload();
                    return;
                }
                tvStatus.setText(st.route == ServerLink.Route.WIFI ? "Connected over Wi-Fi" : "Not connected");
                tvStep.setText(st.detail);
                btnRetry.setText("Check again");
                btnRetry.setVisibility(View.VISIBLE);
                double mb = new File(dir, "dataset.mp4").length() / (1024.0 * 1024.0);
                if (st.route == ServerLink.Route.WIFI) {
                    new AlertDialog.Builder(this)
                        .setTitle("Upload over Wi-Fi?")
                        .setMessage(String.format(Locale.US, "The USB cable is not connected, so this %.0f MB "
                            + "recording would go over Wi-Fi to %s. That is slower and can drop.\n\nFor the cable: "
                            + "plug the phone into the PC running the server (USB debugging on), then tap Check "
                            + "again.", mb, ServerLink.hostOf(st.url)))
                        .setPositiveButton("Upload over Wi-Fi", (d, w) -> {
                            btnRetry.setVisibility(View.GONE);
                            startUpload();
                        })
                        .setNeutralButton("Check again", (d, w) -> checkThenUpload())
                        .setNegativeButton("Not now", null)
                        .show();
                } else {
                    new AlertDialog.Builder(this)
                        .setTitle("Not connected to the server")
                        .setMessage(st.detail + "\n\nConnect the phone with a USB cable to the PC running the "
                            + "server (USB debugging on), or join the same Wi-Fi as the server. Then tap Check "
                            + "again. The recording stays on the phone (Scans tab).")
                        .setPositiveButton("Check again", (d, w) -> checkThenUpload())
                        .setNeutralButton("Server settings",
                            (d, w) -> startActivity(new android.content.Intent(this, ServerActivity.class)))
                        .setNegativeButton("Not now", null)
                        .show();
                }
            });
        }).start();
    }

    /** Stop button (Back while uploading): asks, then cancels the running upload. */
    private void stopUpload() {
        new AlertDialog.Builder(this)
            .setTitle("Stop the upload?")
            .setMessage("What was sent so far is not kept on the server. The recording stays on the phone (Scans tab).")
            .setPositiveButton("Stop", (d, w) -> {
                stopRequested = true;
                okhttp3.Call c = uploadCall;
                if (c != null) c.cancel();
            })
            .setNegativeButton("Keep uploading", null)
            .show();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        okhttp3.Call c = uploadCall;
        if (c != null) c.cancel();
        polling = false;
        handler.removeCallbacksAndMessages(null);
    }

    private void startUpload() {
        tvStatus.setText("Uploading dataset...");
        tvStep.setText("Preparing files...");
        progressBar.setIndeterminate(true);
        stopRequested = false;
        uploading = true;
        btnBack.setText("Stop upload");

        new Thread(() -> {
            try {
                runOnUiThread(() -> tvStep.setText("Connecting to the server..."));
                ServerLink.State st = ServerLink.resolve(this);
                if (st.route == ServerLink.Route.NONE) {
                    throw new IOException(st.detail);
                }
                serverUrl = st.url;
                final String via = st.routeName();

                File dir = new File(datasetPath);

                File depthDir = new File(dir, "depth");
                File depthZip = null;
                if (depthDir.exists() && depthDir.isDirectory()) {
                    runOnUiThread(() -> tvStep.setText("Zipping depth data..."));
                    depthZip = new File(dir, "depth.zip");
                    zipDirectory(depthDir, depthZip);
                }

                runOnUiThread(() -> tvStep.setText("Uploading via " + via + "..."));

                MultipartBody.Builder builder = new MultipartBody.Builder()
                        .setType(MultipartBody.FORM)
                        .addFormDataPart("iterations", "30000");

                addFilePart(builder, "video", new File(dir, "dataset.mp4"), "video/mp4");
                addFilePart(builder, "poses", new File(dir, "poses.csv"), "text/csv");
                addFilePart(builder, "tracking", new File(dir, "tracking.csv"), "text/csv");
                addFilePart(builder, "points", new File(dir, "points.csv"), "text/csv");
                addFilePart(builder, "quality", new File(dir, "quality.csv"), "text/csv");
                addFilePart(builder, "meta", new File(dir, "meta.json"), "application/json");
                // sensor metadata (exposure, rolling shutter), re-anchor log, lens calibration: optional, sent when recorded
                addFilePart(builder, "camera", new File(dir, "camera.csv"), "text/csv");
                addFilePart(builder, "anchors", new File(dir, "anchors.csv"), "text/csv");
                addFilePart(builder, "lens_metadata", new File(dir, "lens_metadata.json"), "application/json");
                addFilePart(builder, "camera_characteristics", new File(dir, "camera_characteristics.json"), "application/json");

                if (depthZip != null && depthZip.exists()) {
                    addFilePart(builder, "depth_zip", depthZip, "application/zip");
                }

                final long t0 = android.os.SystemClock.elapsedRealtime();
                RequestBody tracked = new GalleryActivity.ProgressRequestBody(builder.build(), (sent, total) -> {
                    double el = Math.max((android.os.SystemClock.elapsedRealtime() - t0) / 1000.0, 0.001);
                    double mbps = sent / 1048576.0 / el;
                    long left = mbps > 0 ? Math.round((total - sent) / 1048576.0 / mbps) : 0;
                    int pct = (int) (sent * 100 / Math.max(total, 1));
                    String line = sent >= total
                            ? "All sent, the server is saving the files..."
                            : String.format(Locale.US, "%.1f / %.1f MB \u00b7 %.1f MB/s \u00b7 %d min %02d s left",
                                sent / 1048576.0, total / 1048576.0, mbps, left / 60, left % 60);
                    runOnUiThread(() -> {
                        progressBar.setIndeterminate(false);
                        progressBar.setProgress(pct);
                        tvStatus.setText("Uploading via " + via + " \u00b7 " + pct + "%");
                        tvStep.setText(line);
                    });
                });
                Request request = new Request.Builder()
                        .url(serverUrl + "/upload")
                        .post(tracked)
                        .build();

                if (stopRequested) throw new IOException("stopped");
                okhttp3.Call call = client.newCall(request);
                uploadCall = call;
                try (Response response = call.execute()) {
                    if (!response.isSuccessful()) {
                        String body = response.body() != null ? response.body().string() : "Unknown error";
                        throw new IOException("Upload failed: " + response.code() + " " + body);
                    }

                    String responseBody = response.body().string();
                    JSONObject json = new JSONObject(responseBody);
                    jobId = json.getString("job_id");

                    uploading = false;
                    runOnUiThread(() -> {
                        btnBack.setText("Back");
                        tvStatus.setText("Processing...");
                        tvStep.setText("Job started: " + jobId);
                        progressBar.setIndeterminate(false);
                        progressBar.setProgress(0);
                        polling = true;
                        pollStatus();
                    });
                }

                if (depthZip != null && depthZip.exists()) {
                    depthZip.delete();
                }

            } catch (Exception e) {
                Log.e(TAG, "Upload failed", e);
                boolean stopped = stopRequested;
                uploading = false;
                runOnUiThread(() -> {
                    btnBack.setText("Back");
                    tvStatus.setText(stopped ? "Upload stopped" : "Upload failed");
                    tvStep.setText(stopped
                            ? "Nothing was kept on the server. The recording stays on the phone (Scans tab)."
                            : "Connection lost or refused: " + e.getMessage()
                                + ". Connect the USB cable or check the Wi-Fi, then tap Retry.");
                    btnRetry.setText("Retry");
                    btnRetry.setVisibility(View.VISIBLE);
                    progressBar.setIndeterminate(false);
                });
            } finally {
                uploadCall = null;
            }
        }).start();
    }

    private void addFilePart(MultipartBody.Builder builder, String name, File file, String mimeType) {
        if (file.exists()) {
            builder.addFormDataPart(name, file.getName(),
                    RequestBody.create(file, MediaType.parse(mimeType)));
        }
    }

    private void pollStatus() {
        if (!polling || jobId == null) return;

        Request request = new Request.Builder()
                .url(serverUrl + "/status/" + jobId)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                handler.postDelayed(() -> pollStatus(), 5000);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                try {
                    String body = response.body().string();
                    JSONObject json = new JSONObject(body);

                    String status = json.optString("status", "unknown");
                    String stepLabel = json.optString("current_step_label", "");
                    int pct = json.optInt("progress_pct", 0);
                    int elapsed = json.optInt("elapsed_sec", 0);
                    String error = json.optString("error", null);
                    JSONArray logs = json.optJSONArray("recent_logs");

                    runOnUiThread(() -> {
                        progressBar.setProgress(pct);
                        tvStep.setText(stepLabel);
                        tvElapsed.setText(formatElapsed(elapsed));

                        if (logs != null && logs.length() > 0) {
                            StringBuilder sb = new StringBuilder();
                            int start = Math.max(0, logs.length() - 8);
                            for (int i = start; i < logs.length(); i++) {
                                sb.append(logs.optString(i, "")).append("\n");
                            }
                            tvLogs.setText(sb.toString().trim());
                        }

                        switch (status) {
                            case "completed":
                                tvStatus.setText("Processing Complete!");
                                tvStep.setText("3D model is ready");
                                progressBar.setProgress(100);
                                polling = false;
                                break;
                            case "failed":
                                tvStatus.setText("Processing Failed");
                                if (error != null && !error.equals("null")) {
                                    tvStep.setText(error);
                                }
                                polling = false;
                                btnRetry.setVisibility(View.VISIBLE);
                                break;
                            default:
                                tvStatus.setText("Processing... " + pct + "%");
                                break;
                        }
                    });

                    if (polling) {
                        handler.postDelayed(() -> pollStatus(), 3000);
                    }
                } catch (Exception e) {
                    Log.e(TAG, "Error parsing status", e);
                    if (polling) {
                        handler.postDelayed(() -> pollStatus(), 5000);
                    }
                }
            }
        });
    }

    private String formatElapsed(int seconds) {
        int min = seconds / 60;
        int sec = seconds % 60;
        return String.format(Locale.US, "Elapsed: %02d:%02d", min, sec);
    }

    private void zipDirectory(File dir, File zipFile) throws IOException {
        try (ZipOutputStream zos = new ZipOutputStream(new FileOutputStream(zipFile))) {
            File[] files = dir.listFiles();
            if (files == null) return;
            byte[] buffer = new byte[8192];
            for (File f : files) {
                if (!f.isFile()) continue;
                zos.putNextEntry(new ZipEntry("depth/" + f.getName()));
                try (FileInputStream fis = new FileInputStream(f)) {
                    int len;
                    while ((len = fis.read(buffer)) > 0) {
                        zos.write(buffer, 0, len);
                    }
                }
                zos.closeEntry();
            }
        }
    }
}
