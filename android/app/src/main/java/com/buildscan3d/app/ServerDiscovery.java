package com.buildscan3d.app;

import android.content.Context;
import android.content.SharedPreferences;
import android.preference.PreferenceManager;
import android.text.TextUtils;
import android.util.Log;
import java.util.ArrayList;
import java.util.List;
import java.util.Set;

/** Finding upload servers: the Server screen's search, and the list of recently used servers (ServerLink uses it). */
final class ServerDiscovery {
  private static final String TAG = "ServerDiscovery";
  static final String PREF_RECENT_SERVERS = "recent_servers";
  static final int DISCOVERY_PORT = 8001;

  private ServerDiscovery() {}

  /** Remember a server URL (newest first, at most 5) so the search and ServerLink can offer it again. */
  static void rememberServer(Context ctx, String url) {
    SharedPreferences prefs = PreferenceManager.getDefaultSharedPreferences(ctx);
    List<String> recent = new ArrayList<>();
    recent.add(url);
    for (String u : prefs.getString(PREF_RECENT_SERVERS, "").split("\n")) {
      if (!u.isEmpty() && !u.equals(url) && recent.size() < 5) recent.add(u);
    }
    prefs.edit().putString(PREF_RECENT_SERVERS, TextUtils.join("\n", recent)).apply();
  }

  /**
   * Blocking (up to ~11 s): call it off the main thread. Finds servers four ways: (0) the USB cable; then: (1) UDP broadcast "BUILDSCAN_DISCOVER" on port 8001, answered by the server with its URL
   * (works on networks larger than /24, like the lab Wi-Fi); (2) the saved and recently used servers; (3) a sweep of the
   * phone's own /24 on port 8000. Networks that isolate Wi-Fi clients block all three: then type the URL.
   */
  static List<String> scan(Context ctx) {
    Set<String> found = java.util.Collections.synchronizedSet(new java.util.LinkedHashSet<>());
    // (0) USB cable: the PC forwards the phone's 127.0.0.1:8000 to its server (adb reverse, scripts/usb_link.sh)
    if (ServerLink.healthy(ServerLink.USB_URL)) found.add(ServerLink.USB_URL);
    try {
      // (1) UDP broadcast
      java.util.Set<java.net.InetAddress> targets = new java.util.LinkedHashSet<>();
      targets.add(java.net.InetAddress.getByName("255.255.255.255"));
      java.util.Set<String> subnets = new java.util.LinkedHashSet<>();
      java.util.Enumeration<java.net.NetworkInterface> interfaces = java.net.NetworkInterface.getNetworkInterfaces();
      while (interfaces != null && interfaces.hasMoreElements()) {
        java.net.NetworkInterface ni = interfaces.nextElement();
        if (ni.isLoopback() || !ni.isUp()) continue;
        for (java.net.InterfaceAddress addr : ni.getInterfaceAddresses()) {
          if (addr.getAddress() instanceof java.net.Inet4Address) {
            if (addr.getBroadcast() != null) targets.add(addr.getBroadcast());
            String ip = addr.getAddress().getHostAddress();
            subnets.add(ip.substring(0, ip.lastIndexOf('.')));
          }
        }
      }
      try (java.net.DatagramSocket udp = new java.net.DatagramSocket()) {
        udp.setBroadcast(true);
        udp.setSoTimeout(500);
        byte[] probe = "BUILDSCAN_DISCOVER".getBytes("UTF-8");
        for (java.net.InetAddress t : targets) {
          try {
            udp.send(new java.net.DatagramPacket(probe, probe.length, t, DISCOVERY_PORT));
          } catch (Exception e) {
            Log.w(TAG, "Discovery broadcast to " + t + " failed", e);
          }
        }
        long until = System.currentTimeMillis() + 2500;
        byte[] buf = new byte[1024];
        while (System.currentTimeMillis() < until) {
          java.net.DatagramPacket reply = new java.net.DatagramPacket(buf, buf.length);
          try {
            udp.receive(reply);
          } catch (java.net.SocketTimeoutException e) {
            continue;
          }
          try {
            org.json.JSONObject j = new org.json.JSONObject(new String(reply.getData(), 0, reply.getLength(), "UTF-8"));
            if ("buildscan3d".equals(j.optString("service"))) found.add(j.getString("url"));
          } catch (Exception e) {
            Log.w(TAG, "Bad discovery reply", e);
          }
        }
      } catch (Exception e) {
        Log.w(TAG, "UDP discovery failed", e);
      }

      // (2) saved + recent servers, (3) sweep of the phone's /24
      java.util.concurrent.ExecutorService executor = java.util.concurrent.Executors.newFixedThreadPool(64);
      android.content.SharedPreferences prefs = android.preference.PreferenceManager.getDefaultSharedPreferences(ctx);
      java.util.Set<String> known = new java.util.LinkedHashSet<>();
      known.add(prefs.getString(ProcessingActivity.PREF_SERVER_URL, ProcessingActivity.DEFAULT_SERVER_URL));
      for (String u : prefs.getString(PREF_RECENT_SERVERS, "").split("\n")) if (!u.isEmpty()) known.add(u);
      for (String u : known) {
        if (!found.contains(u)) executor.submit(() -> { if (ServerLink.healthy(u)) found.add(u); });
      }
      int port = 8000;
      for (String subnet : subnets) {
        for (int i = 1; i <= 254; i++) {
          String ip = subnet + "." + i;
          executor.submit(() -> {
            try (java.net.Socket socket = new java.net.Socket()) {
              socket.connect(new java.net.InetSocketAddress(ip, port), 300);
            } catch (Exception e) {
              return;
            }
            String url = "http://" + ip + ":" + port;
            if (ServerLink.healthy(url)) found.add(url);
          });
        }
      }
      executor.shutdown();
      executor.awaitTermination(8, java.util.concurrent.TimeUnit.SECONDS);
      executor.shutdownNow();
    } catch (Exception e) {
      Log.e(TAG, "Network scan error", e);
    }
    synchronized (found) {
      return new ArrayList<>(found);
    }
  }
}
