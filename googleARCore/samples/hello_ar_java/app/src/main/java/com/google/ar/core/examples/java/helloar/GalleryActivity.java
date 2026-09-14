/*
 * Copyright 2026 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

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

public class GalleryActivity extends AppCompatActivity {

  private static final String TAG = "GalleryActivity";

  private VideoView videoView;
  private TextView tvDatasetInfo;
  private TextView tvTrimRange;
  private TextView tvTrimStatus;
  private SeekBar sbTrimStart;
  private SeekBar sbTrimEnd;
  private Button btnTrimSave;

  private File datasetFile;
  private File posesFile;
  private File pointsFile;

  private int videoDurationMs = 0;
  private int trimStartMs = 0;
  private int trimEndMs = 0;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_gallery);

    ImageButton btnBack = findViewById(R.id.btn_back);
    btnBack.setOnClickListener(v -> finish());

    videoView = findViewById(R.id.video_preview);
    tvDatasetInfo = findViewById(R.id.tv_dataset_info);
    tvTrimRange = findViewById(R.id.tv_trim_range);
    tvTrimStatus = findViewById(R.id.tv_trim_status);
    sbTrimStart = findViewById(R.id.sb_trim_start);
    sbTrimEnd = findViewById(R.id.sb_trim_end);
    btnTrimSave = findViewById(R.id.btn_trim_save);

    datasetFile = new File(getExternalFilesDir(null), "dataset.mp4");
    posesFile = new File(getExternalFilesDir(null), "poses.csv");
    pointsFile = new File(getExternalFilesDir(null), "points.csv");

    loadDataset();

    sbTrimStart.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
      @Override
      public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
        if (fromUser) {
          if (progress >= trimEndMs - 500) {
            trimStartMs = Math.max(0, trimEndMs - 500);
            sbTrimStart.setProgress(trimStartMs);
          } else {
            trimStartMs = progress;
          }
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
          if (progress <= trimStartMs + 500) {
            trimEndMs = Math.min(videoDurationMs, trimStartMs + 500);
            sbTrimEnd.setProgress(trimEndMs);
          } else {
            trimEndMs = progress;
          }
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
      tvDatasetInfo.setText("No dataset found. Please record a dataset first.");
      btnTrimSave.setEnabled(false);
      sbTrimStart.setEnabled(false);
      sbTrimEnd.setEnabled(false);
      return;
    }

    // Set up VideoView
    videoView.setVideoPath(datasetFile.getAbsolutePath());
    MediaController mediaController = new MediaController(this);
    mediaController.setAnchorView(videoView);
    videoView.setMediaController(mediaController);

    // Get Duration
    MediaMetadataRetriever retriever = new MediaMetadataRetriever();
    try {
      retriever.setDataSource(datasetFile.getAbsolutePath());
      String durationStr = retriever.extractMetadata(MediaMetadataRetriever.METADATA_KEY_DURATION);
      if (durationStr != null) {
        videoDurationMs = Integer.parseInt(durationStr);
      }
      retriever.release();
    } catch (Exception e) {
      Log.e(TAG, "Error getting video duration", e);
    }

    int poseCount = countFileLines(posesFile);
    int pointCount = countFileLines(pointsFile);
    double fileSizeMb = (double) datasetFile.length() / (1024 * 1024);

    String info = String.format(Locale.US,
        "Video: %.2f MB  |  Duration: %s  |  Poses: %d  |  Points: %d",
        fileSizeMb, formatMs(videoDurationMs), poseCount, pointCount);
    tvDatasetInfo.setText(info);

    trimStartMs = 0;
    trimEndMs = videoDurationMs;
    sbTrimStart.setMax(videoDurationMs);
    sbTrimStart.setProgress(0);
    sbTrimEnd.setMax(videoDurationMs);
    sbTrimEnd.setProgress(videoDurationMs);

    updateTrimRangeText();
    btnTrimSave.setEnabled(true);
    sbTrimStart.setEnabled(true);
    sbTrimEnd.setEnabled(true);
  }

  private void updateTrimRangeText() {
    int duration = Math.max(0, trimEndMs - trimStartMs);
    String text = String.format(Locale.US,
        "Start: %s  |  End: %s  |  Duration: %s",
        formatMs(trimStartMs), formatMs(trimEndMs), formatMs(duration));
    tvTrimRange.setText(text);
  }

  private String formatMs(int ms) {
    int totalSec = ms / 1000;
    int minutes = totalSec / 60;
    int seconds = totalSec % 60;
    return String.format(Locale.US, "%02d:%02d", minutes, seconds);
  }

  private int countFileLines(File file) {
    if (!file.exists()) return 0;
    int lines = 0;
    try (BufferedReader reader = new BufferedReader(new FileReader(file))) {
      while (reader.readLine() != null) {
        lines++;
      }
    } catch (IOException e) {
      Log.e(TAG, "Error reading lines from " + file.getName(), e);
    }
    return lines;
  }

  private void performTrimming() {
    if (trimStartMs == 0 && trimEndMs == videoDurationMs) {
      Toast.makeText(this, "Select a valid sub-range to trim.", Toast.LENGTH_SHORT).show();
      return;
    }

    tvTrimStatus.setVisibility(View.VISIBLE);
    tvTrimStatus.setText("Trimming video & sensor data...");
    btnTrimSave.setEnabled(false);

    long startUs = trimStartMs * 1000L;
    long endUs = trimEndMs * 1000L;

    new Thread(() -> {
      boolean success = true;
      String errorMsg = null;

      try {
        // 1. Trim Video
        File trimmedVideo = new File(getExternalFilesDir(null), "dataset_trimmed.mp4");
        if (trimmedVideo.exists()) trimmedVideo.delete();

        trimVideo(datasetFile, trimmedVideo, startUs, endUs);

        // Replace original video
        if (datasetFile.delete()) {
          trimmedVideo.renameTo(datasetFile);
        }

        // 2. Trim CSV Sensor Data
        trimCsvFiles(startUs, endUs);

      } catch (Exception e) {
        Log.e(TAG, "Trimming failed", e);
        success = false;
        errorMsg = e.getMessage();
      }

      final boolean isSuccess = success;
      final String finalErrorMsg = errorMsg;

      runOnUiThread(() -> {
        tvTrimStatus.setVisibility(View.GONE);
        if (isSuccess) {
          Toast.makeText(GalleryActivity.this, "Dataset & sensor data trimmed successfully!", Toast.LENGTH_LONG).show();
          loadDataset();
        } else {
          Toast.makeText(GalleryActivity.this, "Trimming failed: " + finalErrorMsg, Toast.LENGTH_LONG).show();
          btnTrimSave.setEnabled(true);
        }
      });
    }).start();
  }

  @SuppressWarnings("WrongConstant")
  private void trimVideo(File input, File output, long startUs, long endUs) throws IOException {
    MediaExtractor extractor = new MediaExtractor();
    extractor.setDataSource(input.getAbsolutePath());

    int trackIndex = -1;
    MediaFormat format = null;
    for (int i = 0; i < extractor.getTrackCount(); i++) {
      MediaFormat f = extractor.getTrackFormat(i);
      String mime = f.getString(MediaFormat.KEY_MIME);
      if (mime != null && mime.startsWith("video/")) {
        trackIndex = i;
        format = f;
        break;
      }
    }

    if (trackIndex < 0 || format == null) {
      extractor.release();
      throw new IOException("No video track found in " + input.getName());
    }

    extractor.selectTrack(trackIndex);
    extractor.seekTo(startUs, MediaExtractor.SEEK_TO_CLOSEST_SYNC);

    MediaMuxer muxer = new MediaMuxer(output.getAbsolutePath(), MediaMuxer.OutputFormat.MUXER_OUTPUT_MPEG_4);
    int muxerTrackIndex = muxer.addTrack(format);
    muxer.start();

    int maxBufferSize = format.containsKey(MediaFormat.KEY_MAX_INPUT_SIZE)
        ? format.getInteger(MediaFormat.KEY_MAX_INPUT_SIZE)
        : 1024 * 1024;
    ByteBuffer buffer = ByteBuffer.allocateDirect(maxBufferSize);
    MediaCodec.BufferInfo bufferInfo = new MediaCodec.BufferInfo();

    long ptsOffset = -1;

    while (true) {
      int sampleSize = extractor.readSampleData(buffer, 0);
      if (sampleSize < 0) {
        break;
      }
      long sampleTimeUs = extractor.getSampleTime();
      if (sampleTimeUs > endUs) {
        break;
      }
      if (sampleTimeUs >= startUs) {
        if (ptsOffset < 0) {
          ptsOffset = sampleTimeUs;
        }
        bufferInfo.offset = 0;
        bufferInfo.size = sampleSize;
        bufferInfo.presentationTimeUs = sampleTimeUs - ptsOffset;
        bufferInfo.flags = extractor.getSampleFlags();
        muxer.writeSampleData(muxerTrackIndex, buffer, bufferInfo);
      }
      extractor.advance();
    }

    muxer.stop();
    muxer.release();
    extractor.release();
  }

  private void trimCsvFiles(long startUs, long endUs) {
    if (!posesFile.exists()) return;

    // Find first timestamp in poses.csv
    long firstPoseTs = -1;
    try (BufferedReader reader = new BufferedReader(new FileReader(posesFile))) {
      String line;
      while ((line = reader.readLine()) != null) {
        line = line.trim();
        if (line.isEmpty()) continue;
        String[] parts = line.split(",");
        if (parts.length > 0) {
          try {
            firstPoseTs = Long.parseLong(parts[0]);
            break;
          } catch (NumberFormatException e) {
            // Ignore header or malformed line
          }
        }
      }
    } catch (IOException e) {
      Log.e(TAG, "Error reading first pose timestamp", e);
    }

    if (firstPoseTs < 0) return;

    // Target timestamp range in nanoseconds (ARCore timestamps are in nanoseconds)
    long targetStartNs = firstPoseTs + (startUs * 1000L);
    long targetEndNs = firstPoseTs + (endUs * 1000L);

    // 1. Trim poses.csv
    filterCsvFileByTimestamp(posesFile, targetStartNs, targetEndNs);

    // 2. Trim points.csv
    if (pointsFile.exists()) {
      filterCsvFileByTimestamp(pointsFile, targetStartNs, targetEndNs);
    }
  }

  private void filterCsvFileByTimestamp(File csvFile, long startNs, long endNs) {
    File tempFile = new File(csvFile.getParent(), csvFile.getName() + ".tmp");
    try (BufferedReader reader = new BufferedReader(new FileReader(csvFile));
         BufferedWriter writer = new BufferedWriter(new FileWriter(tempFile))) {

      String line;
      while ((line = reader.readLine()) != null) {
        String trimmed = line.trim();
        if (trimmed.isEmpty()) continue;
        String[] parts = trimmed.split(",");
        if (parts.length > 0) {
          try {
            long ts = Long.parseLong(parts[0]);
            if (ts >= startNs && ts <= endNs) {
              writer.write(line);
              writer.newLine();
            }
          } catch (NumberFormatException e) {
            // Write non-numeric lines (like CSV headers) unconditionally
            writer.write(line);
            writer.newLine();
          }
        }
      }
      writer.flush();
    } catch (IOException e) {
      Log.e(TAG, "Error filtering CSV file: " + csvFile.getName(), e);
    }

    if (tempFile.exists()) {
      if (csvFile.delete()) {
        tempFile.renameTo(csvFile);
      }
    }
  }
}
