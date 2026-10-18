package com.google.ar.core.examples.java.helloar;

import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Date;
import java.util.HashSet;
import java.util.List;
import java.util.Locale;
import java.util.Set;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

public class GalleryActivity extends AppCompatActivity {

  private static final String TAG = "GalleryActivity";
  private static final String PREF_UPLOADED = "uploaded_scans";

  private ListView listView;
  private TextView tvEmpty;
  private TextView tvScanCount;
  private List<File> scanDirs = new ArrayList<>();
  private Set<String> uploadedScans;
  private SharedPreferences prefs;
  private ScanAdapter adapter;
  private final Handler handler = new Handler(Looper.getMainLooper());

  // Track upload state per scan
  private final java.util.Map<String, Integer> uploadProgress = new java.util.concurrent.ConcurrentHashMap<>();
  private final java.util.Map<String, String> uploadStatus = new java.util.concurrent.ConcurrentHashMap<>();

  private final OkHttpClient client = new OkHttpClient.Builder()
      .connectTimeout(15, java.util.concurrent.TimeUnit.SECONDS)
      .writeTimeout(600, java.util.concurrent.TimeUnit.SECONDS)
      .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
      .build();

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_gallery);

    prefs = PreferenceManager.getDefaultSharedPreferences(this);
    uploadedScans = new HashSet<>(prefs.getStringSet(PREF_UPLOADED, new HashSet<>()));

    ImageButton btnBack = findViewById(R.id.btn_back);
    btnBack.setOnClickListener(v -> finish());

    listView = findViewById(R.id.lv_scans);
    tvEmpty = findViewById(R.id.tv_empty);
    tvScanCount = findViewById(R.id.tv_scan_count);

    adapter = new ScanAdapter();
    listView.setAdapter(adapter);

    loadScans();
  }

  @Override
  protected void onResume() {
    super.onResume();
    loadScans();
  }

  private void loadScans() {
    scanDirs.clear();
    File rootDir = getExternalFilesDir(null);
    if (rootDir != null) {
      File[] dirs = rootDir.listFiles((dir, name) ->
          name.startsWith("Scan_") && new File(dir, name).isDirectory());
      if (dirs != null) {
        Arrays.sort(dirs, (a, b) -> Long.compare(b.lastModified(), a.lastModified()));
        Collections.addAll(scanDirs, dirs);
      }
    }

    tvScanCount.setText(scanDirs.size() + " scans");
    tvEmpty.setVisibility(scanDirs.isEmpty() ? View.VISIBLE : View.GONE);
    listView.setVisibility(scanDirs.isEmpty() ? View.GONE : View.VISIBLE);
    adapter.notifyDataSetChanged();
  }

  private String getScanInfo(File dir) {
    File video = new File(dir, "dataset.mp4");
    File poses = new File(dir, "poses.csv");
    StringBuilder sb = new StringBuilder();

    if (video.exists()) {
      double mb = video.length() / (1024.0 * 1024.0);
      sb.append(String.format(Locale.US, "%.1f MB", mb));
    } else {
      sb.append("No video");
    }

    if (poses.exists()) {
      int lines = countLines(poses);
      sb.append(String.format(Locale.US, "  |  %d poses", lines));
    }

    String name = dir.getName();
    if (name.startsWith("Scan_") && name.length() >= 20) {
      try {
        String ts = name.substring(5);
        Date date = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).parse(ts);
        sb.append("  |  ").append(new SimpleDateFormat("MMM dd, HH:mm", Locale.US).format(date));
      } catch (Exception ignored) {}
    }
    return sb.toString();
  }

  private int countLines(File f) {
    int count = 0;
    try (java.io.BufferedReader r = new java.io.BufferedReader(new java.io.FileReader(f))) {
      while (r.readLine() != null) count++;
    } catch (IOException ignored) {}
    return count;
  }

  private boolean isUploaded(File dir) {
    return uploadedScans.contains(dir.getName());
  }

  private void markUploaded(File dir) {
    uploadedScans.add(dir.getName());
    prefs.edit().putStringSet(PREF_UPLOADED, uploadedScans).apply();
  }

  private void deleteScan(File dir, int position) {
    new AlertDialog.Builder(this)
        .setTitle("Delete Scan")
        .setMessage("Delete " + dir.getName() + "? This cannot be undone.")
        .setPositiveButton("Delete", (d, w) -> {
          deleteRecursive(dir);
          uploadedScans.remove(dir.getName());
          prefs.edit().putStringSet(PREF_UPLOADED, uploadedScans).apply();
          loadScans();
          Toast.makeText(this, "Scan deleted", Toast.LENGTH_SHORT).show();
        })
        .setNegativeButton("Cancel", null)
        .show();
  }

  private void deleteRecursive(File f) {
    if (f.isDirectory()) {
      File[] children = f.listFiles();
      if (children != null) {
        for (File child : children) deleteRecursive(child);
      }
    }
    f.delete();
  }

  private void startUpload(File dir) {
    String key = dir.getName();
    if ("uploading".equals(uploadStatus.get(key))) {
      Toast.makeText(this, "Already uploading", Toast.LENGTH_SHORT).show();
      return;
    }

    String serverUrl = prefs.getString(ProcessingActivity.PREF_SERVER_URL,
        ProcessingActivity.DEFAULT_SERVER_URL);

    uploadStatus.put(key, "uploading");
    uploadProgress.put(key, 0);
    adapter.notifyDataSetChanged();

    new Thread(() -> {
      try {
        File depthDir = new File(dir, "depth");
        File depthZip = null;
        if (depthDir.exists() && depthDir.isDirectory()) {
          updateUploadUI(key, 5, "Zipping depth data...");
          depthZip = new File(dir, "depth.zip");
          zipDirectory(depthDir, depthZip);
        }

        updateUploadUI(key, 10, "Uploading...");

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

        RequestBody requestBody = builder.build();
        long totalBytes = requestBody.contentLength();

        // Wrap in a progress-tracking body
        RequestBody trackedBody = new ProgressRequestBody(requestBody, (bytesWritten, contentLength) -> {
          int pct = (int) (10 + (bytesWritten * 85.0 / contentLength));
          updateUploadUI(key, pct, String.format(Locale.US,
              "Uploading... %.1f / %.1f MB",
              bytesWritten / (1024.0 * 1024.0),
              contentLength / (1024.0 * 1024.0)));
        });

        Request request = new Request.Builder()
            .url(serverUrl + "/upload")
            .post(trackedBody)
            .build();

        try (Response response = client.newCall(request).execute()) {
          if (!response.isSuccessful()) {
            String body = response.body() != null ? response.body().string() : "Unknown error";
            throw new IOException("Server error: " + response.code() + " " + body);
          }
        }

        if (depthZip != null && depthZip.exists()) {
          depthZip.delete();
        }

        uploadStatus.put(key, "done");
        uploadProgress.put(key, 100);
        handler.post(() -> {
          markUploaded(dir);
          adapter.notifyDataSetChanged();
          Toast.makeText(this, "Upload complete!", Toast.LENGTH_SHORT).show();
        });

      } catch (Exception e) {
        Log.e(TAG, "Upload failed", e);
        uploadStatus.put(key, "failed");
        handler.post(() -> {
          adapter.notifyDataSetChanged();
          Toast.makeText(this, "Upload failed: " + e.getMessage(), Toast.LENGTH_LONG).show();
        });
      }
    }).start();
  }

  private void updateUploadUI(String key, int pct, String text) {
    uploadProgress.put(key, pct);
    uploadStatus.put(key, text);
    handler.post(() -> adapter.notifyDataSetChanged());
  }

  private void addFilePart(MultipartBody.Builder builder, String name, File file, String mimeType) {
    if (file.exists()) {
      builder.addFormDataPart(name, file.getName(),
          RequestBody.create(file, MediaType.parse(mimeType)));
    }
  }

  private void zipDirectory(File dir, File zipFile) throws IOException {
    try (ZipOutputStream zos = new ZipOutputStream(new FileOutputStream(zipFile))) {
      File[] files = dir.listFiles();
      if (files == null) return;
      byte[] buffer = new byte[65536];
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

  // Adapter
  private class ScanAdapter extends BaseAdapter {
    @Override public int getCount() { return scanDirs.size(); }
    @Override public File getItem(int i) { return scanDirs.get(i); }
    @Override public long getItemId(int i) { return i; }

    @Override
    public View getView(int position, View convertView, ViewGroup parent) {
      if (convertView == null) {
        convertView = getLayoutInflater().inflate(R.layout.item_scan, parent, false);
      }

      File dir = getItem(position);
      String key = dir.getName();

      TextView tvName = convertView.findViewById(R.id.tv_scan_name);
      TextView tvInfo = convertView.findViewById(R.id.tv_scan_info);
      TextView tvBadge = convertView.findViewById(R.id.tv_status_badge);
      ProgressBar pbUpload = convertView.findViewById(R.id.pb_upload);
      TextView tvUploadProg = convertView.findViewById(R.id.tv_upload_progress);
      Button btnPlay = convertView.findViewById(R.id.btn_play);
      Button btnUpload = convertView.findViewById(R.id.btn_upload);
      Button btnTrim = convertView.findViewById(R.id.btn_trim);
      Button btnDelete = convertView.findViewById(R.id.btn_delete);

      // Format name
      String displayName = key;
      if (key.startsWith("Scan_") && key.length() >= 20) {
        try {
          Date d = new SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).parse(key.substring(5));
          displayName = new SimpleDateFormat("MMM dd, yyyy  HH:mm", Locale.US).format(d);
        } catch (Exception ignored) {}
      }
      tvName.setText(displayName);
      tvInfo.setText(getScanInfo(dir));

      // Status badge
      boolean uploaded = isUploaded(dir);
      String status = uploadStatus.get(key);
      if ("uploading".equals(status) || (status != null && status.startsWith("Uploading") || (status != null && status.startsWith("Zipping")))) {
        tvBadge.setText("UPLOADING");
        tvBadge.setBackgroundColor(0xFF2196F3);
        pbUpload.setVisibility(View.VISIBLE);
        tvUploadProg.setVisibility(View.VISIBLE);
        Integer pct = uploadProgress.get(key);
        pbUpload.setProgress(pct != null ? pct : 0);
        tvUploadProg.setText(status);
        btnUpload.setEnabled(false);
        btnUpload.setText("...");
      } else if ("failed".equals(status)) {
        tvBadge.setText("FAILED");
        tvBadge.setBackgroundColor(0xFFFF3B30);
        pbUpload.setVisibility(View.GONE);
        tvUploadProg.setVisibility(View.GONE);
        btnUpload.setEnabled(true);
        btnUpload.setText("Retry");
      } else if (uploaded) {
        tvBadge.setText("UPLOADED");
        tvBadge.setBackgroundColor(0xFF00C853);
        pbUpload.setVisibility(View.GONE);
        tvUploadProg.setVisibility(View.GONE);
        btnUpload.setEnabled(true);
        btnUpload.setText("Re-upload");
      } else {
        tvBadge.setText("LOCAL");
        tvBadge.setBackgroundColor(0xFF78909C);
        pbUpload.setVisibility(View.GONE);
        tvUploadProg.setVisibility(View.GONE);
        btnUpload.setEnabled(true);
        btnUpload.setText("Upload");
      }

      btnPlay.setOnClickListener(v -> {
        Intent intent = new Intent(GalleryActivity.this, ScanDetailActivity.class);
        intent.putExtra("scan_path", dir.getAbsolutePath());
        startActivity(intent);
      });

      btnUpload.setOnClickListener(v -> startUpload(dir));

      btnTrim.setOnClickListener(v -> {
        Intent intent = new Intent(GalleryActivity.this, ScanDetailActivity.class);
        intent.putExtra("scan_path", dir.getAbsolutePath());
        intent.putExtra("open_trim", true);
        startActivity(intent);
      });

      btnDelete.setOnClickListener(v -> deleteScan(dir, position));

      return convertView;
    }
  }

  // Progress-tracking RequestBody wrapper
  static class ProgressRequestBody extends RequestBody {
    private final RequestBody delegate;
    private final ProgressListener listener;

    interface ProgressListener {
      void onProgress(long bytesWritten, long contentLength);
    }

    ProgressRequestBody(RequestBody delegate, ProgressListener listener) {
      this.delegate = delegate;
      this.listener = listener;
    }

    @Override public MediaType contentType() { return delegate.contentType(); }
    @Override public long contentLength() throws IOException { return delegate.contentLength(); }

    @Override
    public void writeTo(okio.BufferedSink sink) throws IOException {
      long total = contentLength();
      okio.ForwardingSink countingSink = new okio.ForwardingSink(sink) {
        long written = 0;
        long lastNotify = 0;
        @Override
        public void write(okio.Buffer source, long byteCount) throws IOException {
          super.write(source, byteCount);
          written += byteCount;
          if (written - lastNotify > 65536) {
            listener.onProgress(written, total);
            lastNotify = written;
          }
        }
      };
      okio.BufferedSink bufferedSink = okio.Okio.buffer(countingSink);
      delegate.writeTo(bufferedSink);
      bufferedSink.flush();
    }
  }
}
