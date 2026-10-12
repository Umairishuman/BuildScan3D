package com.google.ar.core.examples.java.helloar;

import android.content.Context;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.util.AttributeSet;
import android.view.View;

/** Transparent overlay that draws CoverageMap dots (red / yellow / green) over the camera image. */
public class CoverageOverlayView extends View {
  private final Paint paint = new Paint(Paint.ANTI_ALIAS_FLAG);
  private CoverageMap.Projection data = null;

  public CoverageOverlayView(Context context) {
    super(context);
  }

  public CoverageOverlayView(Context context, AttributeSet attrs) {
    super(context, attrs);
  }

  /** Call on the UI thread. null clears the overlay. */
  public void setData(CoverageMap.Projection p) {
    data = p;
    invalidate();
  }

  @Override
  protected void onDraw(Canvas canvas) {
    super.onDraw(canvas);
    CoverageMap.Projection p = data;
    if (p == null || p.n == 0) return;
    float w = getWidth(), h = getHeight();
    float r = Math.max(3f, w / 160f);
    for (int i = 0; i < Math.min(p.n, 2000); i++) {
      paint.setColor(p.colors[i]);
      canvas.drawCircle((p.ndc[2 * i] + 1) * 0.5f * w, (1 - p.ndc[2 * i + 1]) * 0.5f * h, r, paint);
    }
  }
}
