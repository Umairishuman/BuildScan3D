package com.buildscan3d.app;

import android.content.SharedPreferences;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.preference.PreferenceManager;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.appcompat.app.AlertDialog;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.content.ContextCompat;
import java.util.List;

/**
 * Server tab: shows how the phone reaches the upload server right now (ServerLink, every 3 s), how to connect the USB
 * cable, the Wi-Fi server address (type it, or search the network), and the app-update check.
 */
public class ServerActivity extends AppCompatActivity {

  private final Handler handler = new Handler(Looper.getMainLooper());
  private SharedPreferences prefs;
  private TextView tvStatus;
  private TextView tvDetail;
  private EditText etUrl;
  private Button btnSearch;
  private TextView tvSearchStatus;
  private LinearLayout foundList;
  private volatile boolean watching = false;
  private volatile int watchGeneration = 0;

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_server);
    BottomNav.attach(this, BottomNav.Tab.SERVER);
    prefs = PreferenceManager.getDefaultSharedPreferences(this);

    tvStatus = findViewById(R.id.tv_server_status);
    tvDetail = findViewById(R.id.tv_server_detail);
    etUrl = findViewById(R.id.et_server_url);
    btnSearch = findViewById(R.id.btn_search);
    tvSearchStatus = findViewById(R.id.tv_search_status);
    foundList = findViewById(R.id.found_list);

    try {
      String v = getPackageManager().getPackageInfo(getPackageName(), 0).versionName;
      ((TextView) findViewById(R.id.tv_app_version)).setText("v" + v);
    } catch (Exception ignored) {
      // version text stays empty
    }

    String saved = prefs.getString(ProcessingActivity.PREF_SERVER_URL, "");
    if (!saved.isEmpty() && !ServerLink.USB_URL.equals(saved)) etUrl.setText(saved);

    findViewById(R.id.btn_check_now).setOnClickListener(v -> checkOnce());
    findViewById(R.id.btn_save_url).setOnClickListener(v -> saveAndTest());
    btnSearch.setOnClickListener(v -> search());
    findViewById(R.id.btn_updates).setOnClickListener(v -> new UpdateChecker(this).check(true));
  }

  @Override
  protected void onResume() {
    super.onResume();
    watching = true;
    final int gen = ++watchGeneration;
    new Thread(() -> {
      while (watching && gen == watchGeneration) {
        ServerLink.State st = ServerLink.resolve(this);
        handler.post(() -> show(st));
        SystemClock.sleep(3000);
      }
    }, "server-watch").start();
  }

  @Override
  protected void onPause() {
    super.onPause();
    watching = false;
  }

  private void show(ServerLink.State st) {
    tvStatus.setText("●  " + st.label());
    tvStatus.setTextColor(st.color());
    tvDetail.setText(st.detail);
  }

  private void checkOnce() {
    tvStatus.setText("●  Checking connection...");
    tvStatus.setTextColor(ContextCompat.getColor(this, R.color.bs_text_secondary));
    new Thread(() -> {
      ServerLink.State st = ServerLink.resolve(this);
      handler.post(() -> show(st));
    }).start();
  }

  /** "192.168.1.5" -> "http://192.168.1.5:8000"; keeps a scheme and port the user typed. */
  static String normalise(String raw) {
    String u = raw.trim();
    while (u.endsWith("/")) u = u.substring(0, u.length() - 1);
    if (u.isEmpty()) return u;
    if (!u.startsWith("http://") && !u.startsWith("https://")) u = "http://" + u;
    String hostPart = u.replaceFirst("^https?://", "");
    if (!hostPart.contains(":")) u = u + ":8000";
    return u;
  }

  private void saveAndTest() {
    String url = normalise(etUrl.getText().toString());
    if (url.isEmpty()) {
      Toast.makeText(this, "Type the server address first, e.g. 192.168.1.5", Toast.LENGTH_SHORT).show();
      return;
    }
    etUrl.setText(url);
    prefs.edit().putString(ProcessingActivity.PREF_SERVER_URL, url).apply();
    ServerDiscovery.rememberServer(this, url);
    Toast.makeText(this, "Saved. Testing " + url + " ...", Toast.LENGTH_SHORT).show();
    new Thread(() -> {
      boolean ok = ServerLink.healthy(url);
      handler.post(() -> {
        if (ok) {
          Toast.makeText(this, "The server at " + ServerLink.hostOf(url) + " answers.", Toast.LENGTH_LONG).show();
        } else {
          new AlertDialog.Builder(this)
              .setTitle("No answer from " + ServerLink.hostOf(url))
              .setMessage("The address is saved, but the server does not answer. Check that the server is running, "
                  + "that the phone is on the same Wi-Fi as the PC, and that the address is the one the PC shows "
                  + "now (it can change). Or connect the USB cable.")
              .setPositiveButton("OK", null)
              .show();
        }
        checkOnce();
      });
    }).start();
  }

  private void search() {
    btnSearch.setEnabled(false);
    foundList.removeAllViews();
    tvSearchStatus.setVisibility(View.VISIBLE);
    tvSearchStatus.setText("Searching: USB cable, then the network (about 10 s)...");
    new Thread(() -> {
      List<String> found = ServerDiscovery.scan(this);
      handler.post(() -> {
        btnSearch.setEnabled(true);
        if (found.isEmpty()) {
          tvSearchStatus.setText("No server found. Is the server running, and is the phone on the same Wi-Fi? "
              + "Type the address the PC shows, or connect the USB cable.");
          return;
        }
        tvSearchStatus.setText("Found " + found.size() + ": tap one to use it.");
        for (String url : found) {
          Button b = new Button(this, null, android.R.attr.borderlessButtonStyle);
          b.setText(ServerLink.USB_URL.equals(url) ? "USB cable (" + url + ")" : url);
          b.setAllCaps(false);
          b.setTextColor(ContextCompat.getColor(this, R.color.bs_primary));
          b.setBackgroundResource(R.drawable.bg_button_outline);
          LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
              LinearLayout.LayoutParams.MATCH_PARENT, LinearLayout.LayoutParams.WRAP_CONTENT);
          lp.topMargin = 8;
          b.setLayoutParams(lp);
          b.setOnClickListener(v -> {
            if (!ServerLink.USB_URL.equals(url)) {
              etUrl.setText(url);
              prefs.edit().putString(ProcessingActivity.PREF_SERVER_URL, url).apply();
              ServerDiscovery.rememberServer(this, url);
            }
            Toast.makeText(this, "Server: " + url, Toast.LENGTH_SHORT).show();
            checkOnce();
          });
          foundList.addView(b);
        }
      });
    }).start();
  }
}
