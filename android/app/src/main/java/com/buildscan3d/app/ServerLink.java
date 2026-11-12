package com.buildscan3d.app;

import android.content.Context;
import android.content.SharedPreferences;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.preference.PreferenceManager;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;

/**
 * Which way the phone reaches the upload server right now, checked in this order:
 *  1. USB cable: http://127.0.0.1:8000 on the phone is forwarded to the PC by `adb reverse` (scripts/usb_link.sh runs
 *     it while the server runs). Needs no Wi-Fi, IP address or firewall rule, and is the fastest route.
 *  2. Wi-Fi: the saved server URL, then the recently used ones (CaptureActivity.rememberServer).
 * {@link #resolve} blocks for up to a few seconds: call it off the main thread.
 */
final class ServerLink {
  enum Route { USB, WIFI, NONE }

  static final String USB_URL = "http://127.0.0.1:8000";

  /** One check's result: the route, the server URL to use (or the saved one when none answers), and a line for the UI. */
  static final class State {
    final Route route;
    final String url;
    final String detail;

    State(Route route, String url, String detail) {
      this.route = route;
      this.url = url;
      this.detail = detail;
    }

    /** Short text for the status bar, e.g. "Connected · USB cable". */
    String label() {
      switch (route) {
        case USB: return "Connected · USB cable";
        case WIFI: return "Connected · Wi-Fi " + hostOf(url);
        default: return "Not connected";
      }
    }

    /** Status colour: green for USB, blue for Wi-Fi, red when the server cannot be reached. */
    int color() {
      switch (route) {
        case USB: return 0xFF00C853;
        case WIFI: return 0xFF2196F3;
        default: return 0xFFFF3B30;
      }
    }

    String routeName() {
      return route == Route.USB ? "USB" : route == Route.WIFI ? "Wi-Fi" : "no connection";
    }
  }

  private static final OkHttpClient QUICK = new OkHttpClient.Builder()
      .connectTimeout(1500, TimeUnit.MILLISECONDS)
      .readTimeout(2, TimeUnit.SECONDS)
      .build();

  private ServerLink() {}

  /** True if url answers GET /health like our server. */
  static boolean healthy(String url) {
    if (url == null || url.isEmpty()) return false;
    Request req = new Request.Builder().url(url + "/health").build();
    try (Response resp = QUICK.newCall(req).execute()) {
      String body = resp.body() != null ? resp.body().string() : "";
      return resp.isSuccessful() && body.contains("\"ok\"");
    } catch (Exception e) {
      return false;
    }
  }

  /** Finds the route to use now (USB first, then Wi-Fi). Blocking: never call it on the main thread. */
  static State resolve(Context ctx) {
    if (healthy(USB_URL)) {
      return new State(Route.USB, USB_URL, "Phone on the USB cable: uploads go over the cable");
    }
    SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(ctx);
    String saved = prefs.getString(ProcessingActivity.PREF_SERVER_URL, ProcessingActivity.DEFAULT_SERVER_URL);
    Set<String> candidates = new LinkedHashSet<>();
    if (!USB_URL.equals(saved)) candidates.add(saved);
    for (String u : prefs.getString(CaptureActivity.PREF_RECENT_SERVERS, "").split("\n")) {
      if (!u.isEmpty() && !USB_URL.equals(u)) candidates.add(u);
    }
    for (String u : candidates) {
      if (healthy(u)) {
        if (!u.equals(saved)) {
          prefs.edit().putString(ProcessingActivity.PREF_SERVER_URL, u).apply();
        }
        return new State(Route.WIFI, u, "Uploads go over the network to " + hostOf(u));
      }
    }
    return new State(Route.NONE, USB_URL.equals(saved) ? ProcessingActivity.DEFAULT_SERVER_URL : saved,
        whyNot(ctx, saved));
  }

  /** A plain reason why no server answers, from the phone's own network state. */
  private static String whyNot(Context ctx, String saved) {
    String server = USB_URL.equals(saved) ? "the server" : "the server at " + hostOf(saved);
    try {
      ConnectivityManager cm = (ConnectivityManager) ctx.getSystemService(Context.CONNECTIVITY_SERVICE);
      Network net = cm != null ? cm.getActiveNetwork() : null;
      NetworkCapabilities caps = net != null ? cm.getNetworkCapabilities(net) : null;
      if (caps == null) {
        return "No network. Plug in the USB cable, or turn Wi-Fi on.";
      }
      if (caps.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)) {
        return "Wi-Fi is on, but " + server + " does not answer. Is the server running? "
            + "The PC's address may have changed: set it in Server URL, or plug in the USB cable.";
      }
      if (caps.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR)) {
        return "Phone is on mobile data. Join the PC's Wi-Fi or hotspot, or plug in the USB cable.";
      }
      return server.substring(0, 1).toUpperCase() + server.substring(1)
          + " does not answer. Plug in the USB cable, or check the Wi-Fi.";
    } catch (Exception e) {
      return "The server does not answer. Plug in the USB cable, or check the Wi-Fi.";
    }
  }

  /** "http://10.0.0.5:8000" -> "10.0.0.5". */
  static String hostOf(String url) {
    String h = url.replaceFirst("^https?://", "");
    int slash = h.indexOf('/');
    if (slash >= 0) h = h.substring(0, slash);
    int colon = h.lastIndexOf(':');
    return colon > 0 ? h.substring(0, colon) : h;
  }
}
