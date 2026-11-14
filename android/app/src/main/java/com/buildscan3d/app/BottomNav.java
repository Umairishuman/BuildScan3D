package com.buildscan3d.app;

import android.app.Activity;
import android.content.Intent;
import android.content.res.ColorStateList;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import androidx.core.content.ContextCompat;

/**
 * The bottom navigation bar (res/layout/view_bottom_nav.xml) shared by the three main screens. Each tab brings its
 * screen to the front instead of stacking a new copy, so switching tabs keeps each screen as it was.
 */
final class BottomNav {
  enum Tab { CAPTURE, SCANS, SERVER }

  private BottomNav() {}

  /** Wires the bar inside activity a, with tab `current` highlighted. */
  static void attach(Activity a, Tab current) {
    setUp(a, R.id.nav_capture, R.id.nav_capture_icon, R.id.nav_capture_label, Tab.CAPTURE, current,
        CaptureActivity.class);
    setUp(a, R.id.nav_scans, R.id.nav_scans_icon, R.id.nav_scans_label, Tab.SCANS, current, GalleryActivity.class);
    setUp(a, R.id.nav_server, R.id.nav_server_icon, R.id.nav_server_label, Tab.SERVER, current,
        ServerActivity.class);
  }

  /** Shows or hides the bar (hidden on the capture screen while recording). */
  static void setVisible(Activity a, boolean visible) {
    View bar = a.findViewById(R.id.bottom_nav);
    if (bar != null) bar.setVisibility(visible ? View.VISIBLE : View.GONE);
  }

  private static void setUp(Activity a, int itemId, int iconId, int labelId, Tab tab, Tab current,
      Class<? extends Activity> target) {
    View item = a.findViewById(itemId);
    if (item == null) return;
    boolean selected = tab == current;
    int color = ContextCompat.getColor(a, selected ? R.color.bs_primary : R.color.bs_text_secondary);
    ImageView icon = a.findViewById(iconId);
    TextView label = a.findViewById(labelId);
    icon.setImageTintList(ColorStateList.valueOf(color));
    label.setTextColor(color);
    label.setTypeface(null, selected ? android.graphics.Typeface.BOLD : android.graphics.Typeface.NORMAL);
    item.setOnClickListener(v -> {
      if (selected) return;
      Intent i = new Intent(a, target);
      i.addFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT | Intent.FLAG_ACTIVITY_NO_ANIMATION);
      a.startActivity(i);
      a.overridePendingTransition(0, 0);
    });
  }
}
