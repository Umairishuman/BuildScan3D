/*
 * Copyright 2017 Google LLC
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

import android.content.DialogInterface;
import android.content.Intent;
import android.content.res.Resources;
import android.media.Image;
import android.opengl.GLES30;
import android.opengl.GLSurfaceView;
import android.opengl.Matrix;
import android.os.Bundle;
import android.util.Log;
import android.view.MenuItem;
import android.view.MotionEvent;
import android.view.View;
import android.widget.ImageButton;
import android.widget.PopupMenu;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import com.google.ar.core.Anchor;
import com.google.ar.core.ArCoreApk;
import com.google.ar.core.ArCoreApk.Availability;
import com.google.ar.core.Camera;
import com.google.ar.core.CameraConfig;
import com.google.ar.core.CameraConfigFilter;
import com.google.ar.core.Config;
import com.google.ar.core.Config.InstantPlacementMode;
import com.google.ar.core.DepthPoint;
import com.google.ar.core.Frame;
import com.google.ar.core.HitResult;
import com.google.ar.core.InstantPlacementPoint;
import com.google.ar.core.LightEstimate;
import com.google.ar.core.Plane;
import com.google.ar.core.Point;
import com.google.ar.core.Point.OrientationMode;
import com.google.ar.core.PointCloud;
import com.google.ar.core.Pose;
import com.google.ar.core.Session;
import com.google.ar.core.Trackable;
import com.google.ar.core.TrackingFailureReason;
import com.google.ar.core.TrackingState;
import com.google.ar.core.examples.java.common.helpers.CameraPermissionHelper;
import com.google.ar.core.examples.java.common.helpers.DepthSettings;
import com.google.ar.core.examples.java.common.helpers.DisplayRotationHelper;
import com.google.ar.core.examples.java.common.helpers.FullScreenHelper;
import com.google.ar.core.examples.java.common.helpers.InstantPlacementSettings;
import com.google.ar.core.examples.java.common.helpers.SnackbarHelper;
import com.google.ar.core.examples.java.common.helpers.TapHelper;
import com.google.ar.core.examples.java.common.helpers.TrackingStateHelper;
import com.google.ar.core.examples.java.common.samplerender.Framebuffer;
import com.google.ar.core.examples.java.common.samplerender.GLError;
import com.google.ar.core.examples.java.common.samplerender.Mesh;
import com.google.ar.core.examples.java.common.samplerender.SampleRender;
import com.google.ar.core.examples.java.common.samplerender.Shader;
import com.google.ar.core.examples.java.common.samplerender.Texture;
import com.google.ar.core.examples.java.common.samplerender.VertexBuffer;
import com.google.ar.core.examples.java.common.samplerender.arcore.BackgroundRenderer;
import com.google.ar.core.examples.java.common.samplerender.arcore.PlaneRenderer;
import com.google.ar.core.examples.java.common.samplerender.arcore.SpecularCubemapFilter;
import com.google.ar.core.exceptions.CameraNotAvailableException;
import com.google.ar.core.exceptions.NotYetAvailableException;
import com.google.ar.core.exceptions.UnavailableApkTooOldException;
import com.google.ar.core.exceptions.UnavailableArcoreNotInstalledException;
import com.google.ar.core.exceptions.UnavailableDeviceNotCompatibleException;
import com.google.ar.core.exceptions.UnavailableSdkTooOldException;
import com.google.ar.core.exceptions.UnavailableUserDeclinedInstallationException;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;

/**
 * This is a simple example that shows how to create an augmented reality (AR) application using the
 * ARCore API. The application will display any detected planes and will allow the user to tap on a
 * plane to place a 3D model.
 */
public class HelloArActivity extends AppCompatActivity implements SampleRender.Renderer {

  // --- Recording State Variables - BLAZING ---
  private boolean isRecording = false;
  private java.io.File currentDatasetDir;
  private CaptureLogger captureLogger;
  // Live capture IQA
  private final QualityMonitor qualityMonitor = new QualityMonitor();
  private android.widget.TextView qualityText;
  private android.widget.TextView coverageText;
  private long lastQualityUiNs = 0;
  private long lastBuzzMs = 0;
  private QualityMonitor.Level lastLevel = QualityMonitor.Level.GOOD;
  // Live coverage overlay (which surfaces still need filming from more directions)
  private final CoverageMap coverageMap = new CoverageMap();
  private CoverageOverlayView coverageOverlay;
  private long lastCoverageNs = 0;
  private final float[] coverageMvp = new float[16];
  private View recordToggleButton;
  private android.widget.TextView recordTimerText;
  private android.widget.TextView cameraInfoText;
  private com.google.ar.core.CameraConfig selectedCameraConfig = null;
  private boolean userSelectedCameraConfig = false;

  // ADD THE TIMER VARIABLES HERE
  private android.os.Handler timerHandler = new android.os.Handler();
  private long startTime = 0;
  private Runnable timerRunnable = new Runnable() {
    @Override
    public void run() {
      long seconds = (System.currentTimeMillis() - startTime) / 1000;
      String timeStr = String.format("%02d:%02d", seconds / 60, seconds % 60);
      if (recordTimerText != null) {
        recordTimerText.setText(timeStr);
      }
      timerHandler.postDelayed(this, 500);
    }
  };

  private static final String TAG = HelloArActivity.class.getSimpleName();

  private static final String SEARCHING_PLANE_MESSAGE = "Searching for surfaces...";

  private static final float Z_NEAR = 0.1f;
  private static final float Z_FAR = 100f;


  // Rendering. The Renderers are created here, and initialized when the GL surface is created.
  private GLSurfaceView surfaceView;

  private boolean installRequested;

  private Session session;
  private final SnackbarHelper messageSnackbarHelper = new SnackbarHelper();
  private DisplayRotationHelper displayRotationHelper;
  private final TrackingStateHelper trackingStateHelper = new TrackingStateHelper(this);
  private SampleRender render;

  private PlaneRenderer planeRenderer;
  private BackgroundRenderer backgroundRenderer;
  private boolean hasSetTextureNames = false;
  private boolean hasUpdatedCameraInfo = false;

  private final DepthSettings depthSettings = new DepthSettings();
  private boolean[] depthSettingsMenuDialogCheckboxes = new boolean[2];

  // Point Cloud
  private VertexBuffer pointCloudVertexBuffer;
  private Mesh pointCloudMesh;
  private Shader pointCloudShader;
  // Keep track of the last point cloud rendered to avoid updating the VBO if point cloud
  // was not changed.  Do this using the timestamp since we can't compare PointCloud objects.
  private long lastPointCloudTimestamp = 0;

  // Temporary matrix allocated here to reduce number of allocations for each frame.
  private final float[] modelMatrix = new float[16];
  private final float[] viewMatrix = new float[16];
  private final float[] projectionMatrix = new float[16];
  private final float[] modelViewMatrix = new float[16]; // view x model
  private final float[] modelViewProjectionMatrix = new float[16]; // projection x view x model

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    surfaceView = findViewById(R.id.surfaceview);
    displayRotationHelper = new DisplayRotationHelper(/* context= */ this);


    // Set up renderer.
    render = new SampleRender(surfaceView, this, getAssets());

    installRequested = false;

    depthSettings.onCreate(this);
    ImageButton settingsButton = findViewById(R.id.settings_button);
    settingsButton.setOnClickListener(
        new View.OnClickListener() {
          @Override
          public void onClick(View v) {
            PopupMenu popup = new PopupMenu(HelloArActivity.this, v);
            popup.setOnMenuItemClickListener(HelloArActivity.this::settingsMenuClick);
            popup.inflate(R.menu.settings_menu);
            popup.show();
          }
        });

    recordTimerText = findViewById(R.id.tv_record_timer);
    recordToggleButton = findViewById(R.id.btn_record_toggle);
    cameraInfoText = findViewById(R.id.tv_camera_info);
    qualityText = findViewById(R.id.tv_quality);
    coverageText = findViewById(R.id.tv_coverage);
    coverageOverlay = findViewById(R.id.coverage_overlay);

    recordToggleButton.setOnClickListener(
        v -> {
          if (isRecording) {
            stopRecording();
          } else {
            startRecording();
          }
        });

    ImageButton galleryButton = findViewById(R.id.btn_gallery);
    if (galleryButton != null) {
      galleryButton.setOnClickListener(v -> {
        Intent intent = new Intent(HelloArActivity.this, GalleryActivity.class);
        startActivity(intent);
      });
    }

    new UpdateChecker(this).check();
  }

  /** Menu button to launch feature specific settings. */
  protected boolean settingsMenuClick(MenuItem item) {
    if (item.getItemId() == R.id.camera_settings) {
      launchCameraSettingsMenuDialog();
      return true;
    } else if (item.getItemId() == R.id.depth_settings) {
      launchDepthSettingsMenuDialog();
      return true;
    } else if (item.getItemId() == R.id.server_settings) {
      launchServerUrlDialog();
      return true;
    }
    return false;
  }

  private void launchServerUrlDialog() {
    android.content.SharedPreferences prefs = android.preference.PreferenceManager.getDefaultSharedPreferences(this);
    String current = prefs.getString(ProcessingActivity.PREF_SERVER_URL, ProcessingActivity.DEFAULT_SERVER_URL);

    // Build dialog with a scanning list + manual entry
    android.widget.LinearLayout layout = new android.widget.LinearLayout(this);
    layout.setOrientation(android.widget.LinearLayout.VERTICAL);
    layout.setPadding(48, 24, 48, 0);

    android.widget.TextView tvStatus = new android.widget.TextView(this);
    tvStatus.setText("Scanning network for servers...");
    tvStatus.setTextSize(13);
    tvStatus.setPadding(0, 0, 0, 16);
    layout.addView(tvStatus);

    android.widget.LinearLayout listContainer = new android.widget.LinearLayout(this);
    listContainer.setOrientation(android.widget.LinearLayout.VERTICAL);
    layout.addView(listContainer);

    android.widget.TextView tvManual = new android.widget.TextView(this);
    tvManual.setText("Or enter manually:");
    tvManual.setTextSize(13);
    tvManual.setPadding(0, 24, 0, 8);
    layout.addView(tvManual);

    android.widget.EditText input = new android.widget.EditText(this);
    input.setText(current);
    input.setSelectAllOnFocus(true);
    input.setSingleLine();
    input.setTextSize(14);
    layout.addView(input);

    AlertDialog dialog = new AlertDialog.Builder(this)
        .setTitle("Server URL")
        .setView(layout)
        .setPositiveButton("Save", (d, w) -> {
          String url = input.getText().toString().trim();
          if (!url.isEmpty()) {
            prefs.edit().putString(ProcessingActivity.PREF_SERVER_URL, url).apply();
            Toast.makeText(this, "Server: " + url, Toast.LENGTH_SHORT).show();
          }
        })
        .setNegativeButton("Cancel", null)
        .create();
    dialog.show();

    // Scan common subnets for the server in background
    new Thread(() -> {
      List<String> found = scanForServers();
      runOnUiThread(() -> {
        if (found.isEmpty()) {
          tvStatus.setText("No servers found on local network.");
        } else {
          tvStatus.setText("Found " + found.size() + " server(s) — tap to select:");
        }
        listContainer.removeAllViews();
        for (String url : found) {
          android.widget.Button btn = new android.widget.Button(this);
          btn.setText(url);
          btn.setTextSize(13);
          btn.setAllCaps(false);
          btn.setBackgroundColor(0xFF1E1E2E);
          btn.setTextColor(0xFF4FC3F7);
          btn.setPadding(16, 8, 16, 8);
          android.widget.LinearLayout.LayoutParams lp = new android.widget.LinearLayout.LayoutParams(
              android.widget.LinearLayout.LayoutParams.MATCH_PARENT,
              android.widget.LinearLayout.LayoutParams.WRAP_CONTENT);
          lp.setMargins(0, 4, 0, 4);
          btn.setLayoutParams(lp);
          btn.setOnClickListener(v -> {
            input.setText(url);
            prefs.edit().putString(ProcessingActivity.PREF_SERVER_URL, url).apply();
            Toast.makeText(this, "Server: " + url, Toast.LENGTH_SHORT).show();
            dialog.dismiss();
          });
          listContainer.addView(btn);
        }
      });
    }).start();
  }

  private List<String> scanForServers() {
    List<String> results = new ArrayList<>();
    try {
      // Get the device's local IPs to find which subnets to scan
      java.util.Enumeration<java.net.NetworkInterface> interfaces = java.net.NetworkInterface.getNetworkInterfaces();
      java.util.Set<String> subnets = new java.util.LinkedHashSet<>();
      while (interfaces.hasMoreElements()) {
        java.net.NetworkInterface ni = interfaces.nextElement();
        if (ni.isLoopback() || !ni.isUp()) continue;
        for (java.net.InterfaceAddress addr : ni.getInterfaceAddresses()) {
          java.net.InetAddress inet = addr.getAddress();
          if (inet instanceof java.net.Inet4Address) {
            String ip = inet.getHostAddress();
            String subnet = ip.substring(0, ip.lastIndexOf('.'));
            subnets.add(subnet);
          }
        }
      }

      // Scan each subnet in parallel (common IPs first, then sweep .1-.254)
      int port = 8000;
      java.util.concurrent.ExecutorService executor = java.util.concurrent.Executors.newFixedThreadPool(50);
      java.util.concurrent.CopyOnWriteArrayList<String> found = new java.util.concurrent.CopyOnWriteArrayList<>();
      List<java.util.concurrent.Future<?>> futures = new ArrayList<>();

      for (String subnet : subnets) {
        for (int i = 1; i <= 254; i++) {
          String ip = subnet + "." + i;
          futures.add(executor.submit(() -> {
            try {
              java.net.Socket socket = new java.net.Socket();
              socket.connect(new java.net.InetSocketAddress(ip, port), 300);
              socket.close();
              // Verify it's our server by hitting /health
              String url = "http://" + ip + ":" + port;
              okhttp3.OkHttpClient quick = new okhttp3.OkHttpClient.Builder()
                  .connectTimeout(2, java.util.concurrent.TimeUnit.SECONDS)
                  .readTimeout(2, java.util.concurrent.TimeUnit.SECONDS)
                  .build();
              okhttp3.Request req = new okhttp3.Request.Builder().url(url + "/health").build();
              try (okhttp3.Response resp = quick.newCall(req).execute()) {
                if (resp.isSuccessful()) {
                  String body = resp.body() != null ? resp.body().string() : "";
                  if (body.contains("ok")) {
                    found.add(url);
                  }
                }
              }
            } catch (Exception ignored) {}
          }));
        }
      }

      // Wait for all scans (max 5 seconds)
      executor.shutdown();
      executor.awaitTermination(5, java.util.concurrent.TimeUnit.SECONDS);
      results.addAll(found);
    } catch (Exception e) {
      Log.e(TAG, "Network scan error", e);
    }
    return results;
  }

  @Override
  protected void onDestroy() {
    if (session != null) {
      // Explicitly close ARCore Session to release native resources.
      // Review the API reference for important considerations before calling close() in apps with
      // more complicated lifecycle requirements:
      // https://developers.google.com/ar/reference/java/arcore/reference/com/google/ar/core/Session#close()
      session.close();
      session = null;
    }

    super.onDestroy();
  }

  // CODE INJECTION - Blazing (Corrected for High-Res & 60 FPS Selection)
  private void applyCameraSettings(Session session, boolean prefer60Fps) {
    if (userSelectedCameraConfig && selectedCameraConfig != null) {
      try {
        session.setCameraConfig(selectedCameraConfig);
        android.util.Size size = selectedCameraConfig.getImageSize();
        int fps = selectedCameraConfig.getFpsRange().getUpper();
        String cameraInfoStr = String.format(java.util.Locale.US, "%dx%d @ %d FPS", size.getWidth(), size.getHeight(), fps);
        runOnUiThread(() -> {
          if (cameraInfoText != null) {
            cameraInfoText.setText(cameraInfoStr);
          }
        });
      } catch (Exception e) {
        Log.e(TAG, "Error applying user selected camera config", e);
      }
      return;
    }

    CameraConfigFilter filter = new CameraConfigFilter(session);
    if (prefer60Fps) {
      filter.setTargetFps(java.util.EnumSet.of(CameraConfig.TargetFps.TARGET_FPS_60, CameraConfig.TargetFps.TARGET_FPS_30));
    } else {
      filter.setTargetFps(java.util.EnumSet.of(CameraConfig.TargetFps.TARGET_FPS_30));
    }

    List<CameraConfig> supportedConfigs = session.getSupportedCameraConfigs(filter);

    if (supportedConfigs.isEmpty()) {
      // Fallback to all supported configs without TargetFps filter
      supportedConfigs = session.getSupportedCameraConfigs(new CameraConfigFilter(session));
    }

    if (!supportedConfigs.isEmpty()) {
      CameraConfig bestConfig = supportedConfigs.get(0);
      int maxPixels = 0;
      int maxFps = 0;

      // Iterate through all supported configs to find highest resolution AND highest FPS
      for (CameraConfig config : supportedConfigs) {
        android.util.Size imageSize = config.getImageSize();
        int pixels = imageSize.getWidth() * imageSize.getHeight();
        int fps = config.getFpsRange().getUpper();

        Log.i(TAG, "Available CameraConfig: " + imageSize.getWidth() + "x" + imageSize.getHeight() + " FPS range: " + config.getFpsRange());

        if (pixels > maxPixels || (pixels == maxPixels && fps > maxFps)) {
          maxPixels = pixels;
          maxFps = fps;
          bestConfig = config;
        }
      }

      selectedCameraConfig = bestConfig;
      session.setCameraConfig(bestConfig);
      android.util.Size finalSize = bestConfig.getImageSize();
      android.util.Range<Integer> fpsRange = bestConfig.getFpsRange();
      int fps = fpsRange.getUpper();
      String cameraInfoStr = String.format(java.util.Locale.US, "%dx%d @ %d FPS", finalSize.getWidth(), finalSize.getHeight(), fps);
      Log.i(TAG, "Selected Camera Config: " + cameraInfoStr);

      runOnUiThread(() -> {
        if (cameraInfoText != null) {
          cameraInfoText.setText(cameraInfoStr);
        }
      });
    }
  }

  private void launchCameraSettingsMenuDialog() {
    if (session == null) return;

    List<CameraConfig> rawConfigs = session.getSupportedCameraConfigs(new CameraConfigFilter(session));
    if (rawConfigs.isEmpty()) {
      Toast.makeText(this, "No camera configs available", Toast.LENGTH_SHORT).show();
      return;
    }

    // Copy to mutable list because ARCore returns an unmodifiable list
    List<CameraConfig> configs = new ArrayList<>(rawConfigs);

    // Sort by Resolution descending, then FPS descending
    configs.sort((c1, c2) -> {
      int p1 = c1.getImageSize().getWidth() * c1.getImageSize().getHeight();
      int p2 = c2.getImageSize().getWidth() * c2.getImageSize().getHeight();
      if (p1 != p2) {
        return Integer.compare(p2, p1);
      }
      return Integer.compare(c2.getFpsRange().getUpper(), c1.getFpsRange().getUpper());
    });

    String[] displayNames = new String[configs.size()];
    int currentSelectedIndex = 0;

    CameraConfig currentActive = selectedCameraConfig;
    if (currentActive == null) {
      try {
        currentActive = session.getCameraConfig();
      } catch (Exception ignored) {}
    }

    for (int i = 0; i < configs.size(); i++) {
      CameraConfig c = configs.get(i);
      android.util.Size size = c.getImageSize();
      int fps = c.getFpsRange().getUpper();
      displayNames[i] = String.format(java.util.Locale.US, "%dx%d @ %d FPS (FPS range: %d-%d)",
          size.getWidth(), size.getHeight(), fps, c.getFpsRange().getLower(), c.getFpsRange().getUpper());

      if (currentActive != null &&
          c.getImageSize().equals(currentActive.getImageSize()) &&
          c.getFpsRange().equals(currentActive.getFpsRange())) {
        currentSelectedIndex = i;
      }
    }

    final int[] choice = new int[] { currentSelectedIndex };

    new AlertDialog.Builder(this)
        .setTitle("Select Camera Resolution & FPS")
        .setSingleChoiceItems(displayNames, currentSelectedIndex, (dialog, which) -> choice[0] = which)
        .setPositiveButton("Apply", (dialog, which) -> {
          int selected = choice[0];
          if (selected >= 0 && selected < configs.size()) {
            selectedCameraConfig = configs.get(selected);
            userSelectedCameraConfig = true;
            applySelectedCameraConfig();
          }
        })
        .setNegativeButton("Cancel", null)
        .show();
  }



  private void applySelectedCameraConfig() {
    if (session == null || selectedCameraConfig == null) return;
    try {
      displayRotationHelper.onPause();
      surfaceView.onPause();
      session.pause();

      session.setCameraConfig(selectedCameraConfig);

      configureSession();
      session.resume();
      surfaceView.onResume();
      displayRotationHelper.onResume();

      android.util.Size size = selectedCameraConfig.getImageSize();
      int fps = selectedCameraConfig.getFpsRange().getUpper();
      String cameraInfoStr = String.format(java.util.Locale.US, "%dx%d @ %d FPS", size.getWidth(), size.getHeight(), fps);
      if (cameraInfoText != null) {
        cameraInfoText.setText(cameraInfoStr);
      }
      Toast.makeText(this, "Applied Camera Config: " + cameraInfoStr, Toast.LENGTH_SHORT).show();
    } catch (Exception e) {
      Log.e(TAG, "Failed to apply selected camera config", e);
      Toast.makeText(this, "Failed to apply camera config: " + e.getMessage(), Toast.LENGTH_SHORT).show();
    }
  }

  @Override
  protected void onResume() {
    super.onResume();

    if (session == null) {
      Exception exception = null;
      String message = null;
      try {
        // Always check the latest availability.
        Availability availability = ArCoreApk.getInstance().checkAvailability(this);

        // In all other cases, try to install ARCore and handle installation failures.
        if (availability != Availability.SUPPORTED_INSTALLED) {
          switch (ArCoreApk.getInstance().requestInstall(this, !installRequested)) {
            case INSTALL_REQUESTED:
              installRequested = true;
              return;
            case INSTALLED:
              break;
          }
        }

        // ARCore requires camera permissions to operate. If we did not yet obtain runtime
        // permission on Android M and above, now is a good time to ask the user for it.
        if (!CameraPermissionHelper.hasCameraPermission(this)) {
          CameraPermissionHelper.requestCameraPermission(this);
          return;
        }

        // Create the session.
        session = new Session(/* context= */ this);
      } catch (UnavailableArcoreNotInstalledException
               | UnavailableUserDeclinedInstallationException e) {
        message = "Please install ARCore";
        exception = e;
      } catch (UnavailableApkTooOldException e) {
        message = "Please update ARCore";
        exception = e;
      } catch (UnavailableSdkTooOldException e) {
        message = "Please update this app";
        exception = e;
      } catch (UnavailableDeviceNotCompatibleException e) {
        message = "This device does not support AR";
        exception = e;
      } catch (Exception e) {
        message = "Failed to create AR session";
        exception = e;
      }

      if (message != null) {
        messageSnackbarHelper.showError(this, message);
        Log.e(TAG, "Exception creating session", exception);
        return;
      }
    }

    // Note that order matters - see the note in onPause(), the reverse applies here.
    try {
      configureSession();

      // Recording and playback logic has been safely moved to the Start/Stop buttons!

      // Code Injection - Blazing
      applyCameraSettings(session, true);

      hasUpdatedCameraInfo = false;
      session.resume();
    } catch (CameraNotAvailableException e) {
      messageSnackbarHelper.showError(this, "Camera not available. Try restarting the app.");
      session = null;
      return;
    }

    surfaceView.onResume();
    displayRotationHelper.onResume();
  }

  /** Live IQA: evaluate this frame, log it while recording, refresh the banner at ~5 Hz. */
  private void updateQuality(Frame frame, Camera camera) {
    final QualityMonitor.Result q = qualityMonitor.update(frame, camera, isRecording);
    if (isRecording && captureLogger != null) {
      captureLogger.logQuality(q.csv(frame.getTimestamp()));
    }
    // short vibration when quality turns bad while recording (rate-limited)
    long nowMs = System.currentTimeMillis();
    if (isRecording && q.level == QualityMonitor.Level.BAD && lastLevel != QualityMonitor.Level.BAD
        && nowMs - lastBuzzMs > 1500) {
      lastBuzzMs = nowMs;
      android.os.Vibrator vib = (android.os.Vibrator) getSystemService(VIBRATOR_SERVICE);
      if (vib != null && vib.hasVibrator()) {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
          vib.vibrate(android.os.VibrationEffect.createOneShot(80, android.os.VibrationEffect.DEFAULT_AMPLITUDE));
        } else {
          vib.vibrate(80);
        }
      }
    }
    lastLevel = q.level;
    long nowNs = System.nanoTime();
    if (nowNs - lastQualityUiNs < 200_000_000L) return;
    lastQualityUiNs = nowNs;
    final String coverage = isRecording ? qualityMonitor.coverageText() : null;
    runOnUiThread(() -> {
      if (qualityText != null) {
        int color = q.level == QualityMonitor.Level.GOOD ? 0xCC2E7D32
            : q.level == QualityMonitor.Level.WARN ? 0xCCF9A825 : 0xCCC62828;
        qualityText.setBackgroundColor(color);
        qualityText.setText(q.message);
      }
      if (coverageText != null && coverage != null) {
        coverageText.setText(coverage);
      }
    });
  }

  // Code Injection - BLAZING
  private void startRecording() {
    if (session == null) return;
    try {
      String timestamp = new java.text.SimpleDateFormat("yyyyMMdd_HHmmss", java.util.Locale.getDefault()).format(new java.util.Date());
      currentDatasetDir = new java.io.File(getExternalFilesDir(null), "Scan_" + timestamp);
      if (!currentDatasetDir.exists()) {
          currentDatasetDir.mkdirs();
      }

      java.io.File dest = new java.io.File(currentDatasetDir, "dataset.mp4");
      try {
        captureLogger = new CaptureLogger(currentDatasetDir);
        coverageMap.clear();
        captureLogger.setCoverage(coverageMap);
        captureLogger.writeCameraCharacteristics(this, session);
      } catch (java.io.IOException e) {
        Log.e(TAG, "Failed to open capture logs", e);
        return;
      }

      com.google.ar.core.RecordingConfig recordingConfig = new com.google.ar.core.RecordingConfig(session)
              .setMp4DatasetUri(android.net.Uri.fromFile(dest))
              .setAutoStopOnPause(true);

      session.startRecording(recordingConfig);
      qualityMonitor.resetSession();
      isRecording = true;
      if (coverageText != null) {
        coverageText.setVisibility(View.VISIBLE);
      }

      // START THE TIMER
      startTime = System.currentTimeMillis();
      timerHandler.postDelayed(timerRunnable, 0);

      // Update UI
      if (recordTimerText != null) {
        recordTimerText.setVisibility(View.VISIBLE);
      }
      if (recordToggleButton != null) {
        recordToggleButton.animate().scaleX(0.7f).scaleY(0.7f).setDuration(200).start();
        recordToggleButton.setBackgroundResource(R.drawable.bg_record_active);
      }
      Toast.makeText(this, "Recording Started", Toast.LENGTH_SHORT).show();
    } catch (com.google.ar.core.exceptions.RecordingFailedException e) {
      Log.e(TAG, "Failed to start recording", e);
      Toast.makeText(this, "Failed to start recording", Toast.LENGTH_SHORT).show();
    }
  }

  private void stopRecording() {
    if (session == null) return;
    try {
      isRecording = false;
      session.stopRecording();
      if (captureLogger != null) {
        captureLogger.close();
        captureLogger = null;
      }
      final String summary = qualityMonitor.summary() + "\n" + coverageMap.summary();
      runOnUiThread(() -> {
        if (coverageOverlay != null) {
          coverageOverlay.setData(null);
        }
      });
      runOnUiThread(() -> {
        if (coverageText != null) {
          coverageText.setVisibility(View.GONE);
        }
        final String datasetPath = currentDatasetDir != null ? currentDatasetDir.getAbsolutePath() : null;
        new AlertDialog.Builder(this).setTitle("Capture quality").setMessage(summary)
            .setPositiveButton("Upload & Process", (d, w) -> {
              if (datasetPath != null) {
                Intent intent = new Intent(HelloArActivity.this, ProcessingActivity.class);
                intent.putExtra("dataset_path", datasetPath);
                startActivity(intent);
              }
            })
            .setNeutralButton("Gallery", (d, w) -> {
              Intent intent = new Intent(HelloArActivity.this, GalleryActivity.class);
              startActivity(intent);
            })
            .setNegativeButton("Close", null).show();
      });

      // STOP THE TIMER AND RESET TEXT
      timerHandler.removeCallbacks(timerRunnable);
      if (recordTimerText != null) {
        recordTimerText.setVisibility(View.INVISIBLE);
        recordTimerText.setText("00:00");
      }

      // Update UI
      if (recordToggleButton != null) {
        recordToggleButton.animate().scaleX(1.0f).scaleY(1.0f).setDuration(200).start();
        recordToggleButton.setBackgroundResource(R.drawable.bg_record_ready);
      }
      Toast.makeText(this, "Recording Saved to Storage", Toast.LENGTH_LONG).show();
    } catch (Exception e) {
      Log.e(TAG, "Failed to stop recording", e);
    }
  }

  @Override
  public void onPause() {
    super.onPause();
    if (session != null) {
      // Note that the order matters - GLSurfaceView is paused first so that it does not try
      // to query the session. If Session is paused before GLSurfaceView, GLSurfaceView may
      // still call session.update() and get a SessionPausedException.
      displayRotationHelper.onPause();
      surfaceView.onPause();
      session.pause();
    }
  }

  @Override
  public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] results) {
    super.onRequestPermissionsResult(requestCode, permissions, results);
    if (!CameraPermissionHelper.hasCameraPermission(this)) {
      // Use toast instead of snackbar here since the activity will exit.
      Toast.makeText(this, "Camera permission is needed to run this application", Toast.LENGTH_LONG)
          .show();
      if (!CameraPermissionHelper.shouldShowRequestPermissionRationale(this)) {
        // Permission denied with checking "Do not ask again".
        CameraPermissionHelper.launchPermissionSettings(this);
      }
      finish();
    }
  }

  @Override
  public void onWindowFocusChanged(boolean hasFocus) {
    super.onWindowFocusChanged(hasFocus);
    FullScreenHelper.setFullScreenOnWindowFocusChanged(this, hasFocus);
  }

  @Override
  public void onSurfaceCreated(SampleRender render) {
    // Prepare the rendering objects. This involves reading shaders and 3D model files, so may throw
    // an IOException.
    try {
      planeRenderer = new PlaneRenderer(render);
      backgroundRenderer = new BackgroundRenderer(render);
      // Point cloud
      pointCloudShader =
          Shader.createFromAssets(
                  render,
                  "shaders/point_cloud.vert",
                  "shaders/point_cloud.frag",
                  /* defines= */ null)
              .setVec4(
                  "u_Color", new float[] {31.0f / 255.0f, 188.0f / 255.0f, 210.0f / 255.0f, 1.0f})
              .setFloat("u_PointSize", 5.0f);
      // four entries per vertex: X, Y, Z, confidence
      pointCloudVertexBuffer =
          new VertexBuffer(render, /* numberOfEntriesPerVertex= */ 4, /* entries= */ null);
      final VertexBuffer[] pointCloudVertexBuffers = {pointCloudVertexBuffer};
      pointCloudMesh =
          new Mesh(
              render, Mesh.PrimitiveMode.POINTS, /* indexBuffer= */ null, pointCloudVertexBuffers);

    } catch (IOException e) {
      Log.e(TAG, "Failed to read a required asset file", e);
      messageSnackbarHelper.showError(this, "Failed to read a required asset file: " + e);
    }
  }

  @Override
  public void onSurfaceChanged(SampleRender render, int width, int height) {
    displayRotationHelper.onSurfaceChanged(width, height);
  }

  @Override
  public void onDrawFrame(SampleRender render) {
    if (session == null) {
      return;
    }

    // Texture names should only be set once on a GL thread unless they change. This is done during
    // onDrawFrame rather than onSurfaceCreated since the session is not guaranteed to have been
    // initialized during the execution of onSurfaceCreated.
    if (!hasSetTextureNames) {
      session.setCameraTextureNames(
              new int[] {backgroundRenderer.getCameraColorTexture().getTextureId()});
      hasSetTextureNames = true;
    }

    if (!hasUpdatedCameraInfo) {
      try {
        CameraConfig activeConfig = session.getCameraConfig();
        if (activeConfig != null) {
          android.util.Size size = activeConfig.getImageSize();
          android.util.Range<Integer> fpsRange = activeConfig.getFpsRange();
          int fps = fpsRange.getUpper();
          String infoStr = String.format(java.util.Locale.US, "%dx%d @ %d FPS", size.getWidth(), size.getHeight(), fps);
          runOnUiThread(() -> {
            if (cameraInfoText != null) {
              cameraInfoText.setText(infoStr);
            }
          });
          hasUpdatedCameraInfo = true;
        }
      } catch (Exception e) {
        Log.e(TAG, "Error updating camera info text", e);
      }
    }

    // -- Update per-frame state

    // Notify ARCore session that the view size changed so that the perspective matrix and
    // the video background can be properly adjusted.
    displayRotationHelper.updateSessionIfNeeded(session);

    // Obtain the current frame from the AR Session. When the configuration is set to
    // UpdateMode.BLOCKING (it is by default), this will throttle the rendering to the
    // camera framerate.
    Frame frame;
    try {
      frame = session.update();
    } catch (CameraNotAvailableException e) {
      Log.e(TAG, "Camera not available during onDrawFrame", e);
      messageSnackbarHelper.showError(this, "Camera not available. Try restarting the app.");
      return;
    } catch (Exception e) {
      Log.e(TAG, "Exception during session.update()", e);
      return;
    }
    Camera camera = frame.getCamera();

    // Code Injection - BLAZING
    // --- START POSE DUMP --- (buffered, written off the GL thread by CaptureLogger)
    if (isRecording && captureLogger != null) {
      captureLogger.onFrame(session, frame, camera);
    }
    updateQuality(frame, camera);
    // --- END POSE DUMP ---

    // Update BackgroundRenderer state to match the depth settings.
    try {
      backgroundRenderer.setUseDepthVisualization(
              render, depthSettings.depthColorVisualizationEnabled());
      backgroundRenderer.setUseOcclusion(render, depthSettings.useDepthForOcclusion());
    } catch (IOException e) {
      Log.e(TAG, "Failed to read a required asset file", e);
      messageSnackbarHelper.showError(this, "Failed to read a required asset file: " + e);
      return;
    }
    // BackgroundRenderer.updateDisplayGeometry must be called every frame to update the coordinates
    // used to draw the background camera image.
    backgroundRenderer.updateDisplayGeometry(frame);

    // Draw camera feed before the recording early-return so the screen stays live
    if (frame.getTimestamp() != 0) {
      backgroundRenderer.drawBackground(render);
    }

    // During recording, skip demo rendering (planes, objects, lighting) to save GPU for capture
    if (isRecording) {
      camera.getProjectionMatrix(projectionMatrix, 0, Z_NEAR, Z_FAR);
      camera.getViewMatrix(viewMatrix, 0);
      if (coverageOverlay != null && System.nanoTime() - lastCoverageNs > 500_000_000L) {
        lastCoverageNs = System.nanoTime();
        Matrix.multiplyMM(coverageMvp, 0, projectionMatrix, 0, viewMatrix, 0);
        final CoverageMap.Projection proj = coverageMap.project(coverageMvp, camera.getPose().getTranslation());
        runOnUiThread(() -> coverageOverlay.setData(proj));
      }
      try (PointCloud pointCloud = frame.acquirePointCloud()) {
        if (pointCloud.getTimestamp() > lastPointCloudTimestamp) {
          lastPointCloudTimestamp = pointCloud.getTimestamp();
          if (captureLogger != null) {
            captureLogger.onPointCloud(pointCloud);
          }
        }
      }
      return;
    }

    if (camera.getTrackingState() == TrackingState.TRACKING
            && (depthSettings.useDepthForOcclusion()
            || depthSettings.depthColorVisualizationEnabled())) {
      try (Image depthImage = frame.acquireDepthImage16Bits()) {
        backgroundRenderer.updateCameraDepthTexture(depthImage);
      } catch (NotYetAvailableException e) {
        // This normally means that depth data is not available yet. This is normal so we will not
        // spam the logcat with this.
      }
    }

    // Keep the screen unlocked while tracking, but allow it to lock when tracking stops.
    trackingStateHelper.updateKeepScreenOnFlag(camera.getTrackingState());

    // Show a message based on whether tracking has failed, if planes are detected, and if the user
    // has placed any objects.
    String message = null;
    if (camera.getTrackingState() == TrackingState.PAUSED) {
      if (camera.getTrackingFailureReason() == TrackingFailureReason.NONE) {
        message = SEARCHING_PLANE_MESSAGE;
      } else {
        message = TrackingStateHelper.getTrackingFailureReasonString(camera);
      }
    }
    if (message == null) {
      messageSnackbarHelper.hide(this);
    } else {
      messageSnackbarHelper.showMessage(this, message);
    }

    // If not tracking, don't draw 3D objects.
    if (camera.getTrackingState() == TrackingState.PAUSED) {
      return;
    }

    // -- Draw non-occluded virtual objects (planes, point cloud)

    // Get projection matrix.
    camera.getProjectionMatrix(projectionMatrix, 0, Z_NEAR, Z_FAR);

    // Get camera matrix and draw.
    camera.getViewMatrix(viewMatrix, 0);

    // Live coverage overlay (~5 Hz while recording)
    if (isRecording && coverageOverlay != null && System.nanoTime() - lastCoverageNs > 500_000_000L) {
      lastCoverageNs = System.nanoTime();
      Matrix.multiplyMM(coverageMvp, 0, projectionMatrix, 0, viewMatrix, 0);
      final CoverageMap.Projection proj = coverageMap.project(coverageMvp, camera.getPose().getTranslation());
      runOnUiThread(() -> coverageOverlay.setData(proj));
    }

    // Code Injection - BLAZING
    // Visualize tracked points.
    // Use try-with-resources to automatically release the point cloud.
    try (PointCloud pointCloud = frame.acquirePointCloud()) {
      if (pointCloud.getTimestamp() > lastPointCloudTimestamp) {
        pointCloudVertexBuffer.set(pointCloud.getPoints());
        lastPointCloudTimestamp = pointCloud.getTimestamp();

        // --- START POINT CLOUD DUMP ---
        if (isRecording && captureLogger != null) {
          captureLogger.onPointCloud(pointCloud);
        }
        // --- END POINT CLOUD DUMP ---
      }

      Matrix.multiplyMM(modelViewProjectionMatrix, 0, projectionMatrix, 0, viewMatrix, 0);
      pointCloudShader.setMat4("u_ModelViewProjection", modelViewProjectionMatrix);
      render.draw(pointCloudMesh, pointCloudShader);
    }

    // Visualize planes.
    planeRenderer.drawPlanes(
            render,
            session.getAllTrackables(Plane.class),
            camera.getDisplayOrientedPose(),
            projectionMatrix);

  }

  /** Shows checkboxes to the user to facilitate toggling of depth-based effects. */
  private void launchDepthSettingsMenuDialog() {
    // Retrieves the current settings to show in the checkboxes.
    resetSettingsMenuDialogCheckboxes();

    // Shows the dialog to the user.
    Resources resources = getResources();
    if (session.isDepthModeSupported(Config.DepthMode.AUTOMATIC)) {
      // With depth support, the user can select visualization options.
      new AlertDialog.Builder(this)
          .setTitle(R.string.options_title_with_depth)
          .setMultiChoiceItems(
              resources.getStringArray(R.array.depth_options_array),
              depthSettingsMenuDialogCheckboxes,
              (DialogInterface dialog, int which, boolean isChecked) ->
                  depthSettingsMenuDialogCheckboxes[which] = isChecked)
          .setPositiveButton(
              R.string.done,
              (DialogInterface dialogInterface, int which) -> applySettingsMenuDialogCheckboxes())
          .setNegativeButton(
              android.R.string.cancel,
              (DialogInterface dialog, int which) -> resetSettingsMenuDialogCheckboxes())
          .show();
    } else {
      // Without depth support, no settings are available.
      new AlertDialog.Builder(this)
          .setTitle(R.string.options_title_without_depth)
          .setPositiveButton(
              R.string.done,
              (DialogInterface dialogInterface, int which) -> applySettingsMenuDialogCheckboxes())
          .show();
    }
  }

  private void applySettingsMenuDialogCheckboxes() {
    depthSettings.setUseDepthForOcclusion(depthSettingsMenuDialogCheckboxes[0]);
    depthSettings.setDepthColorVisualizationEnabled(depthSettingsMenuDialogCheckboxes[1]);
    configureSession();
  }

  private void resetSettingsMenuDialogCheckboxes() {
    depthSettingsMenuDialogCheckboxes[0] = depthSettings.useDepthForOcclusion();
    depthSettingsMenuDialogCheckboxes[1] = depthSettings.depthColorVisualizationEnabled();
  }

  /** Checks if we detected at least one plane. */
  private boolean hasTrackingPlane() {
    for (Plane plane : session.getAllTrackables(Plane.class)) {
      if (plane.getTrackingState() == TrackingState.TRACKING) {
        return true;
      }
    }
    return false;
  }

  /** Configures the session with feature settings. */
  private void configureSession() {
    Config config = session.getConfig();
    // walls need VERTICAL plane finding; ARCore's default config only looks for horizontal planes
    config.setPlaneFindingMode(Config.PlaneFindingMode.HORIZONTAL_AND_VERTICAL);
    // Environmental-HDR light estimation only lights the demo pawn but runs every frame (GPU/CPU load and heat
    // on long captures, which add to dropped camera frames). The capture tool does not need it.
    config.setLightEstimationMode(Config.LightEstimationMode.DISABLED);
    if (session.isDepthModeSupported(Config.DepthMode.AUTOMATIC)) {
      config.setDepthMode(Config.DepthMode.AUTOMATIC);
    } else {
      config.setDepthMode(Config.DepthMode.DISABLED);
    }
    config.setInstantPlacementMode(InstantPlacementMode.DISABLED);
    session.configure(config);
  }
}
