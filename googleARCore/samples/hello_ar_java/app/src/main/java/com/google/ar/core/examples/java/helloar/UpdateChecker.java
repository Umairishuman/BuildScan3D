package com.google.ar.core.examples.java.helloar;

import android.app.Activity;
import android.app.ProgressDialog;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;
import android.util.Log;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.core.content.FileProvider;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Checks GitHub Releases for a newer app version, downloads the APK inside the app and opens Android's installer.
 * Automatic check at start-up stays quiet unless an update exists; the "Check for updates" menu item always reports
 * the result, including errors.
 */
public class UpdateChecker {
    private static final String TAG = "UpdateChecker";
    private static final String GITHUB_API =
            "https://api.github.com/repos/Umairishuman/BuildScan3D/releases/latest";

    private final Activity activity;
    private final OkHttpClient client = new OkHttpClient();

    public UpdateChecker(Activity activity) {
        this.activity = activity;
    }

    /** Quiet check (app start): only shows something when an update is available. */
    public void check() {
        check(false);
    }

    /** @param manual true when the user asked: also report "up to date" and errors. */
    public void check(boolean manual) {
        if (manual) toast("Checking for updates...");
        Request request = new Request.Builder()
                .url(GITHUB_API)
                .header("Accept", "application/vnd.github.v3+json")
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.w(TAG, "Update check failed", e);
                if (manual) showMessage("Update check failed", "Could not reach GitHub: " + e.getMessage());
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                try (Response r = response) {
                    if (!r.isSuccessful()) {
                        Log.w(TAG, "Update check: HTTP " + r.code());
                        if (manual) showMessage("Update check failed", "GitHub answered HTTP " + r.code() + ".");
                        return;
                    }
                    JSONObject release = new JSONObject(r.body().string());
                    String latestTag = release.getString("tag_name");
                    String latestVersion = latestTag.startsWith("v") ? latestTag.substring(1) : latestTag;
                    String currentVersion = getCurrentVersion();
                    if (currentVersion == null) return;

                    if (isNewer(latestVersion, currentVersion)) {
                        String apkUrl = findApkUrl(release);
                        String pageUrl = release.getString("html_url");
                        activity.runOnUiThread(() -> showUpdateDialog(latestTag, apkUrl, pageUrl));
                    } else if (manual) {
                        showMessage("Up to date", "You have the latest version (" + currentVersion + ").");
                    }
                } catch (Exception e) {
                    Log.w(TAG, "Error parsing release info", e);
                    if (manual) showMessage("Update check failed", "Could not read the release: " + e.getMessage());
                }
            }
        });
    }

    private String getCurrentVersion() {
        try {
            PackageInfo info = activity.getPackageManager().getPackageInfo(activity.getPackageName(), 0);
            return info.versionName;
        } catch (Exception e) {
            return null;
        }
    }

    static boolean isNewer(String remote, String local) {
        String[] r = remote.split("\\.");
        String[] l = local.split("\\.");
        int len = Math.max(r.length, l.length);
        for (int i = 0; i < len; i++) {
            int rv = i < r.length ? parseIntSafe(r[i]) : 0;
            int lv = i < l.length ? parseIntSafe(l[i]) : 0;
            if (rv > lv) return true;
            if (rv < lv) return false;
        }
        return false;
    }

    private static int parseIntSafe(String s) {
        try { return Integer.parseInt(s.trim()); }
        catch (NumberFormatException e) { return 0; }
    }

    private String findApkUrl(JSONObject release) {
        try {
            JSONArray assets = release.getJSONArray("assets");
            for (int i = 0; i < assets.length(); i++) {
                JSONObject asset = assets.getJSONObject(i);
                if (asset.getString("name").endsWith(".apk")) return asset.getString("browser_download_url");
            }
        } catch (Exception e) {
            Log.w(TAG, "No APK asset found in release", e);
        }
        return null;
    }

    private void showUpdateDialog(String version, String apkUrl, String pageUrl) {
        AlertDialog.Builder b = new AlertDialog.Builder(activity)
                .setTitle("Update available")
                .setMessage("BuildScan 3D " + version + " is available. Install it now? Your recordings are kept.")
                .setNegativeButton("Later", null);
        if (apkUrl != null) {
            b.setPositiveButton("Install", (d, w) -> downloadAndInstall(apkUrl, version));
        } else {
            b.setPositiveButton("Open page", (d, w) ->
                    activity.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(pageUrl))));
        }
        b.show();
    }

    private void downloadAndInstall(String apkUrl, String version) {
        // Android 8+: the user must allow this app to install updates (once).
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                && !activity.getPackageManager().canRequestPackageInstalls()) {
            new AlertDialog.Builder(activity)
                    .setTitle("Allow updates")
                    .setMessage("To install updates, allow BuildScan 3D to install apps on the next screen, "
                            + "then come back and choose Check for updates again.")
                    .setPositiveButton("Open settings", (d, w) -> activity.startActivity(
                            new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                                    Uri.parse("package:" + activity.getPackageName()))))
                    .setNegativeButton("Cancel", null)
                    .show();
            return;
        }

        ProgressDialog progress = new ProgressDialog(activity);
        progress.setTitle("Downloading " + version);
        progress.setProgressStyle(ProgressDialog.STYLE_HORIZONTAL);
        progress.setMax(100);
        progress.setCancelable(false);
        progress.show();

        File dir = new File(activity.getExternalFilesDir(null), "updates");
        dir.mkdirs();
        File apk = new File(dir, "BuildScan3D-update.apk");

        client.newCall(new Request.Builder().url(apkUrl).build()).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                activity.runOnUiThread(progress::dismiss);
                showMessage("Download failed", e.getMessage());
            }

            @Override
            public void onResponse(Call call, Response response) {
                try (Response r = response) {
                    if (!r.isSuccessful()) throw new IOException("HTTP " + r.code());
                    long total = r.body().contentLength();
                    try (InputStream in = r.body().byteStream(); OutputStream out = new FileOutputStream(apk)) {
                        byte[] buf = new byte[64 * 1024];
                        long got = 0;
                        int n;
                        while ((n = in.read(buf)) > 0) {
                            out.write(buf, 0, n);
                            got += n;
                            if (total > 0) {
                                int pct = (int) (100 * got / total);
                                activity.runOnUiThread(() -> progress.setProgress(pct));
                            }
                        }
                    }
                    activity.runOnUiThread(() -> {
                        progress.dismiss();
                        install(apk);
                    });
                } catch (Exception e) {
                    Log.w(TAG, "Update download failed", e);
                    activity.runOnUiThread(progress::dismiss);
                    showMessage("Download failed", String.valueOf(e.getMessage()));
                }
            }
        });
    }

    private void install(File apk) {
        try {
            Uri uri = FileProvider.getUriForFile(activity, activity.getPackageName() + ".updates", apk);
            Intent intent = new Intent(Intent.ACTION_VIEW)
                    .setDataAndType(uri, "application/vnd.android.package-archive")
                    .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_ACTIVITY_NEW_TASK);
            activity.startActivity(intent);
        } catch (Exception e) {
            Log.w(TAG, "Could not start the installer", e);
            showMessage("Install failed", String.valueOf(e.getMessage()));
        }
    }

    private void toast(String msg) {
        activity.runOnUiThread(() -> Toast.makeText(activity, msg, Toast.LENGTH_SHORT).show());
    }

    private void showMessage(String title, String msg) {
        activity.runOnUiThread(() -> new AlertDialog.Builder(activity)
                .setTitle(title).setMessage(msg).setPositiveButton("OK", null).show());
    }
}
