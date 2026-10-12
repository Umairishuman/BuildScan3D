package com.google.ar.core.examples.java.helloar;

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
            .writeTimeout(600, java.util.concurrent.TimeUnit.SECONDS)
            .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
            .build();
    private boolean polling = false;

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

        btnBack.setOnClickListener(v -> finish());
        btnRetry.setOnClickListener(v -> {
            btnRetry.setVisibility(View.GONE);
            startUpload();
        });

        serverUrl = PreferenceManager.getDefaultSharedPreferences(this)
                .getString(PREF_SERVER_URL, DEFAULT_SERVER_URL);

        datasetPath = getIntent().getStringExtra("dataset_path");
        if (datasetPath == null || datasetPath.isEmpty()) {
            tvStatus.setText("Error: No dataset path provided");
            return;
        }

        startUpload();
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        polling = false;
        handler.removeCallbacksAndMessages(null);
    }

    private void startUpload() {
        tvStatus.setText("Uploading dataset...");
        tvStep.setText("Preparing files...");
        progressBar.setIndeterminate(true);

        new Thread(() -> {
            try {
                File dir = new File(datasetPath);

                File depthDir = new File(dir, "depth");
                File depthZip = null;
                if (depthDir.exists() && depthDir.isDirectory()) {
                    runOnUiThread(() -> tvStep.setText("Zipping depth data..."));
                    depthZip = new File(dir, "depth.zip");
                    zipDirectory(depthDir, depthZip);
                }

                runOnUiThread(() -> tvStep.setText("Uploading to server..."));

                MultipartBody.Builder builder = new MultipartBody.Builder()
                        .setType(MultipartBody.FORM)
                        .addFormDataPart("iterations", "30000");

                addFilePart(builder, "video", new File(dir, "dataset.mp4"), "video/mp4");
                addFilePart(builder, "poses", new File(dir, "poses.csv"), "text/csv");
                addFilePart(builder, "tracking", new File(dir, "tracking.csv"), "text/csv");
                addFilePart(builder, "points", new File(dir, "points.csv"), "text/csv");
                addFilePart(builder, "quality", new File(dir, "quality.csv"), "text/csv");
                addFilePart(builder, "meta", new File(dir, "meta.json"), "application/json");

                if (depthZip != null && depthZip.exists()) {
                    addFilePart(builder, "depth_zip", depthZip, "application/zip");
                }

                Request request = new Request.Builder()
                        .url(serverUrl + "/upload")
                        .post(builder.build())
                        .build();

                try (Response response = client.newCall(request).execute()) {
                    if (!response.isSuccessful()) {
                        String body = response.body() != null ? response.body().string() : "Unknown error";
                        throw new IOException("Upload failed: " + response.code() + " " + body);
                    }

                    String responseBody = response.body().string();
                    JSONObject json = new JSONObject(responseBody);
                    jobId = json.getString("job_id");

                    runOnUiThread(() -> {
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
                runOnUiThread(() -> {
                    tvStatus.setText("Upload Failed");
                    tvStep.setText(e.getMessage());
                    btnRetry.setVisibility(View.VISIBLE);
                    progressBar.setIndeterminate(false);
                });
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
