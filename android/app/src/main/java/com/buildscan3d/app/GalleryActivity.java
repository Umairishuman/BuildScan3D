package com.buildscan3d.app;

import android.content.Intent;
import android.content.SharedPreferences;
import android.content.res.ColorStateList;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.preference.PreferenceManager;
import android.util.Log;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowManager;
import android.widget.BaseAdapter;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
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
  // Why the last upload of a scan failed, shown under it
  private final java.util.Map<String, String> uploadError = new java.util.concurrent.ConcurrentHashMap<>();
  // Automatic restarts after a lost connection: count per scan, and the scans waiting for the server to come back
  private static final int MAX_AUTO_RETRIES = 3;
  private final java.util.Map<String, Integer> autoRetries = new java.util.concurrent.ConcurrentHashMap<>();
  private final Set<String> waitingForLink = java.util.concurrent.ConcurrentHashMap.newKeySet();
  private final java.util.concurrent.atomic.AtomicInteger activeUploads = new java.util.concurrent.atomic.AtomicInteger();
  // Stop button: the running request per scan, and the scans the user asked to stop
  private final java.util.Map<String, okhttp3.Call> calls = new java.util.concurrent.ConcurrentHashMap<>();
  private final Set<String> stopRequested = java.util.concurrent.ConcurrentHashMap.newKeySet();
  /** Files the server needs in every upload (server/main.py /upload). */
  private static final String[] REQUIRED_FILES = {
      "dataset.mp4", "poses.csv", "tracking.csv", "points.csv", "quality.csv", "meta.json"};

  // Connection to the server (ServerLink), refreshed every 3 s while this screen is open
  private TextView tvLinkStatus;
  private TextView tvLinkDetail;
  private volatile boolean watchingLink = false;
  private volatile int watchGeneration = 0;  // a newer watcher makes an older one stop

  // A dropped connection fails within 30 s instead of hanging for 10 min; the server may take a while to answer
  // after the last byte (it saves the files), hence the longer read timeout.
  private final OkHttpClient client = new OkHttpClient.Builder()
      .connectTimeout(5, java.util.concurrent.TimeUnit.SECONDS)
      .writeTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
      .readTimeout(120, java.util.concurrent.TimeUnit.SECONDS)
      .build();

  /** The server answered the upload with an error: retrying will not help, so no automatic restart. */
  static class ServerRefusedException extends IOException {
    ServerRefusedException(String msg) { super(msg); }
  }

  /** The user tapped Stop. */
  static class StoppedException extends IOException {
    StoppedException() { super("stopped"); }
  }

  /** No route to the server when the upload was about to start. */
  static class NoLinkException extends IOException {
    NoLinkException(String msg) { super(msg); }
  }

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
    tvLinkStatus = findViewById(R.id.tv_link_status);
    tvLinkDetail = findViewById(R.id.tv_link_detail);
    findViewById(R.id.link_bar).setOnClickListener(v -> startActivity(new Intent(this, ServerActivity.class)));
    BottomNav.attach(this, BottomNav.Tab.SCANS);

    adapter = new ScanAdapter();
    listView.setAdapter(adapter);

    loadScans();
  }

  @Override
  protected void onResume() {
    super.onResume();
    loadScans();
    startLinkWatch();
  }

  @Override
  protected void onPause() {
    super.onPause();
    watchingLink = false;
  }

  /** Checks the connection every 3 s, shows it in the bar, and restarts uploads that lost their connection. */
  private void startLinkWatch() {
    watchingLink = true;
    final int gen = ++watchGeneration;
    new Thread(() -> {
      while (watchingLink && gen == watchGeneration) {
        ServerLink.State st = ServerLink.resolve(this);
        handler.post(() -> showLink(st));
        if (st.route != ServerLink.Route.NONE && !waitingForLink.isEmpty()) {
          for (String key : new ArrayList<>(waitingForLink)) {
            waitingForLink.remove(key);
            File dir = new File(getExternalFilesDir(null), key);
            if (!dir.isDirectory()) continue;
            handler.post(() -> {
              Toast.makeText(this, "Server reachable again (" + st.routeName() + "): restarting the upload",
                  Toast.LENGTH_SHORT).show();
              startUpload(dir, true);
            });
          }
        }
        SystemClock.sleep(3000);
      }
    }, "link-watch").start();
  }

  private void showLink(ServerLink.State st) {
    tvLinkStatus.setText("\u25CF  " + st.label());
    tvLinkStatus.setTextColor(st.color());
    tvLinkDetail.setText(st.detail);
  }

  private int color(int resId) {
    return ContextCompat.getColor(this, resId);
  }

  /** Colours a rounded badge (bg_pill) without losing its shape. */
  private static void tint(View v, int color) {
    v.setBackgroundTintList(ColorStateList.valueOf(color));
  }

  /** Keeps the screen on while an upload runs, so the phone does not sleep and drop Wi-Fi mid-upload. */
  private void keepScreenOn() {
    if (activeUploads.get() > 0) {
      getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    } else {
      getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
    }
  }

  private static String formatDuration(double seconds) {
    long s = Math.max(0, Math.round(seconds));
    return s < 60 ? s + " s" : String.format(Locale.US, "%d min %02d s", s / 60, s % 60);
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

  /** True while a scan is being checked, prepared or sent. */
  private static boolean isBusy(String status) {
    return status != null && (status.equals("uploading") || status.startsWith("Uploading")
        || status.startsWith("Zipping") || status.startsWith("Connecting") || status.startsWith("Checking"));
  }

  /** Files from REQUIRED_FILES that are missing or empty in this recording. */
  private static List<String> missingFiles(File dir) {
    List<String> missing = new ArrayList<>();
    for (String name : REQUIRED_FILES) {
      File f = new File(dir, name);
      if (!f.isFile() || f.length() == 0) missing.add(name);
    }
    return missing;
  }

  /**
   * Upload button. Checks before anything is sent: the recording is complete, then the connection. No server ->
   * asks to connect the USB cable or the Wi-Fi; Wi-Fi only -> offers the faster USB cable first; USB -> uploads.
   */
  private void requestUpload(File dir) {
    String key = dir.getName();
    if (isBusy(uploadStatus.get(key))) return;
    List<String> missing = missingFiles(dir);
    if (!missing.isEmpty()) {
      new AlertDialog.Builder(this)
          .setTitle("This recording is incomplete")
          .setMessage("Missing or empty: " + android.text.TextUtils.join(", ", missing)
              + ".\n\nThe server needs these files. Record the scan again.")
          .setPositiveButton("OK", null)
          .show();
      return;
    }
    uploadStatus.put(key, "Checking the connection...");
    uploadProgress.put(key, 0);
    adapter.notifyDataSetChanged();
    new Thread(() -> {
      ServerLink.State st = ServerLink.resolve(this);
      handler.post(() -> {
        uploadStatus.remove(key);
        adapter.notifyDataSetChanged();
        showLink(st);
        if (isFinishing()) return;
        double mb = new File(dir, "dataset.mp4").length() / (1024.0 * 1024.0);
        if (st.route == ServerLink.Route.USB) {
          startUpload(dir, false);
        } else if (st.route == ServerLink.Route.WIFI) {
          new AlertDialog.Builder(this)
              .setTitle("Upload over Wi-Fi?")
              .setMessage(String.format(Locale.US, "The USB cable is not connected, so this %.0f MB recording would "
                  + "go over Wi-Fi to %s. That is slower and can drop.\n\nFor the cable: plug the phone into the "
                  + "PC running the server (USB debugging on), then tap Check again.", mb, ServerLink.hostOf(st.url)))
              .setPositiveButton("Upload over Wi-Fi", (d, w) -> startUpload(dir, false))
              .setNeutralButton("Check again", (d, w) -> requestUpload(dir))
              .setNegativeButton("Cancel", null)
              .show();
        } else {
          new AlertDialog.Builder(this)
              .setTitle("Not connected to the server")
              .setMessage(st.detail + "\n\nConnect the phone with a USB cable to the PC running the server "
                  + "(USB debugging on), or join the same Wi-Fi as the server. Then tap Check again.")
              .setPositiveButton("Check again", (d, w) -> requestUpload(dir))
              .setNeutralButton("Server settings", (d, w) -> startActivity(new Intent(this, ServerActivity.class)))
              .setNegativeButton("Cancel", null)
              .show();
        }
      });
    }).start();
  }

  /** Stop button: cancels a running upload, or a restart that is waiting for the connection. */
  private void stopUpload(String key) {
    if (waitingForLink.remove(key)) {
      autoRetries.remove(key);
      uploadStatus.put(key, "stopped");
      uploadError.put(key, "Automatic restart cancelled. Tap Upload to send it again.");
      adapter.notifyDataSetChanged();
      return;
    }
    new AlertDialog.Builder(this)
        .setTitle("Stop the upload?")
        .setMessage("What was sent so far is not kept on the server; uploading again starts from the beginning.")
        .setPositiveButton("Stop", (d, w) -> {
          stopRequested.add(key);
          okhttp3.Call c = calls.get(key);
          if (c != null) c.cancel();
          Toast.makeText(this, "Stopping the upload...", Toast.LENGTH_SHORT).show();
        })
        .setNegativeButton("Keep uploading", null)
        .show();
  }

  private void startUpload(File dir) {
    startUpload(dir, false);
  }

  /** auto = restarted by the link watcher after a lost connection (keeps the restart count). */
  private void startUpload(File dir, boolean auto) {
    String key = dir.getName();
    String current = uploadStatus.get(key);
    if (isBusy(current)) {
      Toast.makeText(this, "Already uploading", Toast.LENGTH_SHORT).show();
      return;
    }
    if (!auto) autoRetries.remove(key);
    stopRequested.remove(key);
    waitingForLink.remove(key);
    uploadError.remove(key);

    uploadStatus.put(key, "uploading");
    uploadProgress.put(key, 0);
    adapter.notifyDataSetChanged();
    activeUploads.incrementAndGet();
    keepScreenOn();

    new Thread(() -> {
      try {
        updateUploadUI(key, 0, "Connecting to the server...");
        ServerLink.State st = ServerLink.resolve(this);
        handler.post(() -> showLink(st));
        if (st.route == ServerLink.Route.NONE) {
          throw new NoLinkException(st.detail);
        }
        String serverUrl = st.url;
        String via = st.routeName();
        if (stopRequested.contains(key)) throw new StoppedException();

        File depthDir = new File(dir, "depth");
        File depthZip = null;
        if (depthDir.exists() && depthDir.isDirectory()) {
          updateUploadUI(key, 5, "Zipping depth data...");
          depthZip = new File(dir, "depth.zip");
          zipDirectory(depthDir, depthZip);
        }

        updateUploadUI(key, 10, "Uploading via " + via + "...");

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

        RequestBody requestBody = builder.build();
        long totalBytes = requestBody.contentLength();

        // Wrap in a progress-tracking body
        final long t0 = SystemClock.elapsedRealtime();
        RequestBody trackedBody = new ProgressRequestBody(requestBody, (bytesWritten, contentLength) -> {
          int pct = (int) (10 + (bytesWritten * 85.0 / contentLength));
          double el = Math.max((SystemClock.elapsedRealtime() - t0) / 1000.0, 0.001);
          double mbps = bytesWritten / (1024.0 * 1024.0) / el;
          double left = mbps > 0 ? (contentLength - bytesWritten) / (1024.0 * 1024.0) / mbps : 0;
          String text = bytesWritten >= contentLength
              ? String.format(Locale.US, "Uploading via %s \u00b7 all %.1f MB sent, the server is saving the files...",
                  via, contentLength / (1024.0 * 1024.0))
              : String.format(Locale.US, "Uploading via %s \u00b7 %.1f / %.1f MB \u00b7 %.1f MB/s \u00b7 %s left",
                  via, bytesWritten / (1024.0 * 1024.0), contentLength / (1024.0 * 1024.0), mbps,
                  formatDuration(left));
          updateUploadUI(key, pct, text);
        });

        Request request = new Request.Builder()
            .url(serverUrl + "/upload")
            .post(trackedBody)
            .build();

        if (stopRequested.contains(key)) throw new StoppedException();
        okhttp3.Call call = client.newCall(request);
        calls.put(key, call);
        try (Response response = call.execute()) {
          if (!response.isSuccessful()) {
            String body = response.body() != null ? response.body().string() : "Unknown error";
            throw new ServerRefusedException("Server error: " + response.code() + " " + body);
          }
        } finally {
          calls.remove(key);
        }

        if (depthZip != null && depthZip.exists()) {
          depthZip.delete();
        }

        double secs = (SystemClock.elapsedRealtime() - t0) / 1000.0;
        double mb = totalBytes / (1024.0 * 1024.0);
        String done = String.format(Locale.US, "Upload complete via %s: %.1f MB in %s (%.1f MB/s)",
            via, mb, formatDuration(secs), mb / Math.max(secs, 0.001));
        autoRetries.remove(key);
        uploadStatus.put(key, "done");
        uploadProgress.put(key, 100);
        handler.post(() -> {
          markUploaded(dir);
          adapter.notifyDataSetChanged();
          Toast.makeText(this, done, Toast.LENGTH_LONG).show();
        });

      } catch (Exception e) {
        Log.e(TAG, "Upload failed", e);
        Integer pctNow = uploadProgress.get(key);
        String msg;
        if (stopRequested.remove(key)) {
          autoRetries.remove(key);
          waitingForLink.remove(key);
          uploadError.put(key, String.format(Locale.US,
              "Upload stopped at %d%%. Nothing was kept on the server; tap Upload to send it again.",
              pctNow != null ? pctNow : 0));
          uploadStatus.put(key, "stopped");
          handler.post(() -> adapter.notifyDataSetChanged());
          return;
        } else if (e instanceof ServerRefusedException) {
          msg = "The server refused the upload: " + e.getMessage();
        } else {
          String what = e instanceof NoLinkException ? e.getMessage()
              : String.format(Locale.US, "Connection lost at %d%%.", pctNow != null ? pctNow : 0);
          int n = autoRetries.containsKey(key) ? autoRetries.get(key) : 0;
          if (n < MAX_AUTO_RETRIES) {
            autoRetries.put(key, n + 1);
            waitingForLink.add(key);
            msg = what + " The upload restarts by itself as soon as the server is reachable (restart " + (n + 1)
                + " of " + MAX_AUTO_RETRIES + "). A USB cable is the steadiest link.";
          } else {
            msg = what + " Stopped after " + MAX_AUTO_RETRIES + " automatic restarts: tap Retry.";
          }
        }
        uploadError.put(key, msg);
        uploadStatus.put(key, "failed");
        handler.post(() -> adapter.notifyDataSetChanged());
      } finally {
        activeUploads.decrementAndGet();
        handler.post(this::keepScreenOn);
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
      boolean stopButton = false;
      String err = uploadError.get(key);
      if (isBusy(status)) {
        boolean checking = status.startsWith("Checking");
        tvBadge.setText(checking ? "CHECKING" : "UPLOADING");
        tint(tvBadge, color(R.color.bs_primary));
        pbUpload.setVisibility(View.VISIBLE);
        pbUpload.setIndeterminate(checking);
        tvUploadProg.setVisibility(View.VISIBLE);
        Integer pct = uploadProgress.get(key);
        pbUpload.setProgress(pct != null ? pct : 0);
        tvUploadProg.setTextColor(color(R.color.bs_primary));
        tvUploadProg.setText(status);
        btnUpload.setEnabled(!checking);
        btnUpload.setText(checking ? "..." : "Stop");
        stopButton = !checking;
      } else if ("failed".equals(status)) {
        boolean waiting = waitingForLink.contains(key);
        tvBadge.setText(waiting ? "WAITING" : "FAILED");
        tint(tvBadge, color(waiting ? R.color.bs_warn : R.color.bs_bad));
        pbUpload.setVisibility(View.GONE);
        tvUploadProg.setVisibility(err != null ? View.VISIBLE : View.GONE);
        tvUploadProg.setTextColor(color(waiting ? R.color.bs_warn : R.color.bs_bad));
        tvUploadProg.setText(err != null ? err : "");
        btnUpload.setEnabled(true);
        btnUpload.setText(waiting ? "Stop" : "Retry");
        stopButton = waiting;
      } else if ("stopped".equals(status)) {
        tvBadge.setText("STOPPED");
        tint(tvBadge, color(R.color.bs_neutral));
        pbUpload.setVisibility(View.GONE);
        tvUploadProg.setVisibility(err != null ? View.VISIBLE : View.GONE);
        tvUploadProg.setTextColor(color(R.color.bs_text_secondary));
        tvUploadProg.setText(err != null ? err : "");
        btnUpload.setEnabled(true);
        btnUpload.setText("Upload");
      } else if (uploaded) {
        tvBadge.setText("UPLOADED");
        tint(tvBadge, color(R.color.bs_good));
        pbUpload.setVisibility(View.GONE);
        tvUploadProg.setVisibility(View.GONE);
        btnUpload.setEnabled(true);
        btnUpload.setText("Re-upload");
      } else {
        tvBadge.setText("LOCAL");
        tint(tvBadge, color(R.color.bs_neutral));
        pbUpload.setVisibility(View.GONE);
        tvUploadProg.setVisibility(View.GONE);
        btnUpload.setEnabled(true);
        btnUpload.setText("Upload");
      }
      btnUpload.setBackgroundTintList(stopButton ? ColorStateList.valueOf(color(R.color.bs_bad)) : null);

      btnPlay.setOnClickListener(v -> {
        Intent intent = new Intent(GalleryActivity.this, ScanDetailActivity.class);
        intent.putExtra("scan_path", dir.getAbsolutePath());
        startActivity(intent);
      });

      final boolean stopNow = stopButton;
      btnUpload.setOnClickListener(v -> {
        if (stopNow) {
          stopUpload(key);
        } else {
          requestUpload(dir);
        }
      });

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
        long lastNotifyMs = 0;
        @Override
        public void write(okio.Buffer source, long byteCount) throws IOException {
          super.write(source, byteCount);
          written += byteCount;
          long now = SystemClock.elapsedRealtime();
          if (now - lastNotifyMs >= 250 || written >= total) {
            listener.onProgress(written, total);
            lastNotifyMs = now;
          }
        }
      };
      okio.BufferedSink bufferedSink = okio.Okio.buffer(countingSink);
      delegate.writeTo(bufferedSink);
      bufferedSink.flush();
    }
  }
}
