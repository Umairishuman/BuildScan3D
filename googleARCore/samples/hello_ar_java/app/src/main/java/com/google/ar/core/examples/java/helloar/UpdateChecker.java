package com.google.ar.core.examples.java.helloar;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.net.Uri;
import android.util.Log;
import androidx.appcompat.app.AlertDialog;
import java.io.IOException;
import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.json.JSONArray;
import org.json.JSONObject;

public class UpdateChecker {
    private static final String TAG = "UpdateChecker";
    private static final String GITHUB_API =
            "https://api.github.com/repos/Umairishuman/FYP/releases/latest";

    private final Activity activity;
    private final OkHttpClient client = new OkHttpClient();

    public UpdateChecker(Activity activity) {
        this.activity = activity;
    }

    public void check() {
        Request request = new Request.Builder()
                .url(GITHUB_API)
                .header("Accept", "application/vnd.github.v3+json")
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                Log.w(TAG, "Update check failed", e);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                try {
                    if (!response.isSuccessful()) return;
                    String body = response.body().string();
                    JSONObject release = new JSONObject(body);
                    String latestTag = release.getString("tag_name");
                    String latestVersion = latestTag.startsWith("v") ? latestTag.substring(1) : latestTag;

                    String currentVersion = getCurrentVersion();
                    if (currentVersion == null) return;

                    if (isNewer(latestVersion, currentVersion)) {
                        String apkUrl = findApkUrl(release);
                        String htmlUrl = release.getString("html_url");
                        String downloadUrl = apkUrl != null ? apkUrl : htmlUrl;

                        activity.runOnUiThread(() -> showUpdateDialog(latestTag, downloadUrl));
                    }
                } catch (Exception e) {
                    Log.w(TAG, "Error parsing release info", e);
                }
            }
        });
    }

    private String getCurrentVersion() {
        try {
            PackageInfo info = activity.getPackageManager()
                    .getPackageInfo(activity.getPackageName(), 0);
            return info.versionName;
        } catch (Exception e) {
            return null;
        }
    }

    private boolean isNewer(String remote, String local) {
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

    private int parseIntSafe(String s) {
        try { return Integer.parseInt(s.trim()); }
        catch (NumberFormatException e) { return 0; }
    }

    private String findApkUrl(JSONObject release) {
        try {
            JSONArray assets = release.getJSONArray("assets");
            for (int i = 0; i < assets.length(); i++) {
                JSONObject asset = assets.getJSONObject(i);
                String name = asset.getString("name");
                if (name.endsWith(".apk")) {
                    return asset.getString("browser_download_url");
                }
            }
        } catch (Exception e) {
            Log.w(TAG, "No APK asset found in release", e);
        }
        return null;
    }

    private void showUpdateDialog(String version, String url) {
        new AlertDialog.Builder(activity)
                .setTitle("Update Available")
                .setMessage("BuildScan 3D " + version + " is available. Would you like to download it?")
                .setPositiveButton("Download", (d, w) -> {
                    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                    activity.startActivity(intent);
                })
                .setNegativeButton("Later", null)
                .show();
    }
}
