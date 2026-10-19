package com.google.ar.core.examples.java.helloar;

import android.media.MediaCodec;
import android.media.MediaExtractor;
import android.media.MediaFormat;
import android.media.MediaMetadataRetriever;
import android.media.MediaMuxer;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.MediaController;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;
import android.widget.VideoView;
import androidx.appcompat.app.AppCompatActivity;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.util.Locale;

public class ScanDetailActivity extends AppCompatActivity {

  private static final String TAG = "ScanDetailActivity";

  private VideoView videoView;
  private TextView tvDatasetInfo;
  private TextView tvTrimRange;
  private TextView tvTrimStatus;
  private SeekBar sbTrimStart;
  private SeekBar sbTrimEnd;
  private Button btnTrimSave;

  private File scanDir;
  private File datasetFile;
  private File posesFile;
  private File pointsFile;

  private int videoDurationMs = 0;
  private int trimStartMs = 0;
  private int trimEndMs = 0;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_scan_detail);

    String path = getIntent().getStringExtra("scan_path");
    if (path == null) { finish(); return; }

    scanDir = new File(path);
    datasetFile = new File(scanDir, "dataset.mp4");
    posesFile = new File(scanDir, "poses.csv");
    pointsFile = new File(scanDir, "points.csv");

    ImageButton btnBack = findViewById(R.id.btn_back);
    btnBack.setOnClickListener(v -> finish());

    TextView tvTitle = findViewById(R.id.tv_title);
    tvTitle.setText(scanDir.getName());

    videoView = findViewById(R.id.video_preview);
    tvDatasetInfo = findViewById(R.id.tv_dataset_info);
    tvTrimRange = findViewById(R.id.tv_trim_range);
    tvTrimStatus = findViewById(R.id.tv_trim_status);
    sbTrimStart = findViewById(R.id.sb_trim_start);
    sbTrimEnd = findViewById(R.id.sb_trim_end);
    btnTrimSave = findViewById(R.id.btn_trim_save);

    loadDataset();

    sbTrimStart.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
      @Override
      public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        if (fromUser) {
          trimStartMs = Math.min(progress, trimEndMs - 500);
          if (trimStartMs < 0) trimStartMs = 0;
          sbTrimStart.setProgress(trimStartMs);
          videoView.seekTo(trimStartMs);
          updateTrimRangeText();
        }
      }
      @Override public void onStartTrackingTouch(SeekBar seekBar) {}
      @Override public void onStopTrackingTouch(SeekBar seekBar) {}
    });

    sbTrimEnd.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
      @Override
      public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        if (fromUser) {
          trimEndMs = Math.max(progress, trimStartMs + 500);
          if (trimEndMs > videoDurationMs) trimEndMs = videoDurationMs;
          sbTrimEnd.setProgress(trimEndMs);
          videoView.seekTo(trimEndMs);
          updateTrimRangeText();
        }
      }
      @Override public void onStartTrackingTouch(SeekBar seekBar) {}
      @Override public void onStopTrackingTouch(SeekBar seekBar) {}
    });

    btnTrimSave.setOnClickListener(v -> performTrimming());
  }

  private void loadDataset() {
    if (!datasetFile.exists() || datasetFile.length() == 0) {
      tvDatasetInfo.setText("No video found in this scan.");
      btnTrimSave.setEnabled(false);
      sbTrimStart.setEnabled(false);
      sbTrimEnd.setEnabled(false);
      return;
    }

    videoView.setVideoPath(datasetFile.getAbsolutePath());
    MediaController mc = new MediaController(this);
    mc.setAnchorView(videoView);
    videoView.setMediaController(mc);

    MediaMetadataRetriever retriever = new MediaMetadataRetriever();
    try {
      retriever.setDataSource(datasetFile.getAbsolutePath());
      String dur = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION);
      if (dur != null) videoDurationMs = Integer.parseInt(dur);
      retriever.release();
    } catch (Exception e) {
      Log.e(TAG, "Error getting duration", e);
    }

    int poseCount = countLines(posesFile);
    int pointCount = countLines(pointsFile);
    double mb = datasetFile.length() / (1024.0 * 1024.0);

    tvDatasetInfo.setText(String.format(Locale.US,
        "Video: %.1f MB  |  Duration: %s  |  Poses: %d  |  Points: %d",
        mb, formatMs(videoDurationMs), poseCount, pointCount));

    trimStartMs = 0;
    trimEndMs = videoDurationMs;
    sbTrimStart.setMax(videoDurationMs);
    sbTrimStart.setProgress(0);
    sbTrimEnd.setMax(videoDurationMs);
    sbTrimEnd.setProgress(videoDurationMs);
    updateTrimRangeText();

    videoView.start();
  }

  private void updateTrimRangeText() {
    int dur = Math.max(0, trimEndMs - trimStartMs);
    tvTrimRange.setText(String.format(Locale.US,
        "Start: %s  |  End: %s  |  Duration: %s",
        formatMs(trimStartMs), formatMs(trimEndMs), formatMs(dur)));
  }

  private String formatMs(int ms) {
    int s = ms / 1000;
    return String.format(Locale.US, "%02d:%02d", s / 60, s % 60);
  }

  private int countLines(File f) {
    if (!f.exists()) return 0;
    int n = 0;
    try (BufferedReader r = new BufferedReader(new FileReader(f))) {
      while (r.readLine() != null) n++;
    } catch (IOException ignored) {}
    return n;
  }

  private void performTrimming() {
    if (trimStartMs == 0 && trimEndMs == videoDurationMs) {
      Toast.makeText(this, "Select a sub-range to trim.", Toast.LENGTH_SHORT).show();
      return;
    }

    tvTrimStatus.setVisibility(View.VISIBLE);
    tvTrimStatus.setText("Trimming video & sensor data...");
    btnTrimSave.setEnabled(false);

    long startUs = trimStartMs * 1000L;
    long endUs = trimEndMs * 1000L;

    new Thread(() -> {
      boolean success = true;
      String err = null;
      try {
        File trimmed = new File(scanDir, "dataset_trimmed.mp4");
        if (trimmed.exists()) trimmed.delete();
        trimVideo(datasetFile, trimmed, startUs, endUs);
        if (datasetFile.delete()) trimmed.renameTo(datasetFile);
        trimCsvFiles(startUs, endUs);
      } catch (Exception e) {
        Log.e(TAG, "Trimming failed", e);
        success = false;
        err = e.getMessage();
      }

      final boolean ok = success;
      final String finalErr = err;
      runOnUiThread(() -> {
        tvTrimStatus.setVisibility(View.GONE);
        if (ok) {
          Toast.makeText(this, "Trimmed successfully!", Toast.LENGTH_LONG).show();
          loadDataset();
        } else {
          Toast.makeText(this, "Trim failed: " + finalErr, Toast.LENGTH_LONG).show();
          btnTrimSave.setEnabled(true);
        }
      });
    }).start();
  }

  @SuppressWarnings("WrongConstant")
  private void trimVideo(File input, File output, long startUs, long endUs) throws IOException {
    MediaExtractor ext = new MediaExtractor();
    ext.setDataSource(input.getAbsolutePath());

    int track = -1;
    MediaFormat fmt = null;
    for (int i = 0; i < ext.getTrackCount(); i++) {
      MediaFormat f = ext.getTrackFormat(i);
      String mime = f.getString(MediaFormat.KEY_MIME);
      if (mime != null && mime.startsWith("video/")) { track = i; fmt = f; break; }
    }
    if (track < 0 || fmt == null) { ext.release(); throw new IOException("No video track"); }

    ext.selectTrack(track);
    ext.seekTo(startUs, MediaExtractor.SEEK_TO_CLOSEST_SYNC);

    MediaMuxer mux = new MediaMuxer(output.getAbsolutePath(), MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4);
    int muxTrack = mux.addTrack(fmt);
    mux.start();

    int maxBuf = fmt.containsKey(MediaFormat.KEY_MAX_INPUT_SIZE)
        ? fmt.getInteger(MediaFormat.KEY_MAX_INPUT_SIZE) : 1024 * 1024;
    ByteBuffer buf = ByteBuffer.allocateDirect(maxBuf);
    MediaCodec.BufferInfo info = new MediaCodec.BufferInfo();
    long offset = -1;

    while (true) {
      int size = ext.readSampleData(buf, 0);
      if (size < 0) break;
      long ts = ext.getSampleTime();
      if (ts > endUs) break;
      if (ts >= startUs) {
        if (offset < 0) offset = ts;
        info.offset = 0;
        info.size = size;
        info.presentationTimeUs = ts - offset;
        info.flags = ext.getSampleFlags();
        mux.writeSampleData(muxTrack, buf, info);
      }
      ext.advance();
    }
    mux.stop(); mux.release(); ext.release();
  }

  private void trimCsvFiles(long startUs, long endUs) {
    if (!posesFile.exists()) return;
    long firstTs = -1;
    try (BufferedReader r = new BufferedReader(new FileReader(posesFile))) {
      String line;
      while ((line = r.readLine()) != null) {
        line = line.trim();
        if (line.isEmpty()) continue;
        try { firstTs = Long.parseLong(line.split(",")[0]); break; }
        catch (NumberFormatException ignored) {}
      }
    } catch (IOException ignored) {}
    if (firstTs < 0) return;

    long startNs = firstTs + startUs * 1000L;
    long endNs = firstTs + endUs * 1000L;
    filterCsv(posesFile, startNs, endNs);
    if (pointsFile.exists()) filterCsv(pointsFile, startNs, endNs);
  }

  private void filterCsv(File csv, long startNs, long endNs) {
    File tmp = new File(csv.getParent(), csv.getName() + ".tmp");
    try (BufferedReader r = new BufferedReader(new FileReader(csv));
         BufferedWriter w = new BufferedWriter(new FileWriter(tmp))) {
      String line;
      while ((line = r.readLine()) != null) {
        String t = line.trim();
        if (t.isEmpty()) continue;
        try {
          long ts = Long.parseLong(t.split(",")[0]);
          if (ts >= startNs && ts <= endNs) { w.write(line); w.newLine(); }
        } catch (NumberFormatException e) {
          w.write(line); w.newLine();
        }
      }
    } catch (IOException e) { Log.e(TAG, "Filter CSV error: " + csv.getName(), e); }
    if (tmp.exists() && csv.delete()) tmp.renameTo(csv);
  }
}
