import numpy as np

import common

K = np.array([[500.0, 0, 320], [0, 500.0, 240], [0, 0, 1]])


def test_gl_to_cv_flips_y_and_z():
    assert np.allclose(common.GL_TO_CV, np.diag([1.0, -1.0, -1.0]))


def test_point_in_front_of_camera_projects_to_principal_point():
    u, v, z, ok = common.project(np.array([[0.0, 0.0, -2.0]]), np.eye(4), K, 640, 480)  # OpenGL: -z is forward
    assert ok[0] and np.isclose(z[0], 2.0)
    assert np.isclose(u[0], 320) and np.isclose(v[0], 240)


def test_right_is_plus_u_and_up_is_minus_v():
    u, v, _, ok = common.project(np.array([[0.5, 0.0, -2.0], [0.0, 0.5, -2.0]]), np.eye(4), K, 640, 480)
    assert ok.all()
    assert np.isclose(u[0], 320 + 500 * 0.5 / 2)   # 0.5 m to the right at 2 m depth
    assert np.isclose(v[1], 240 - 500 * 0.5 / 2)   # image y points down, world y points up


def test_point_behind_camera_is_rejected():
    _, _, z, ok = common.project(np.array([[0.0, 0.0, 2.0]]), np.eye(4), K, 640, 480)
    assert z[0] < 0 and not ok[0]


def test_point_outside_image_is_rejected():
    _, _, _, ok = common.project(np.array([[5.0, 0.0, -2.0]]), np.eye(4), K, 640, 480)
    assert not ok[0]


def test_camera_translation_moves_the_projection():
    c2w = np.eye(4)
    c2w[:3, 3] = [1.0, 0.0, 0.0]                      # camera moved 1 m to +x
    u, v, z, ok = common.project(np.array([[1.0, 0.0, -2.0]]), c2w, K, 640, 480)
    assert ok[0] and np.isclose(u[0], 320) and np.isclose(v[0], 240) and np.isclose(z[0], 2.0)
