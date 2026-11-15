#version 300 es
// Coverage voxel dots (CoverageMap): round points in one colour per draw call.
precision mediump float;

uniform vec4 u_Color;

out vec4 o_FragColor;

void main() {
  vec2 d = gl_PointCoord - vec2(0.5);
  if (dot(d, d) > 0.25) discard;
  o_FragColor = u_Color;
}
