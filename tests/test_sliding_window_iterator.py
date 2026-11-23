import numpy as np
import pytest

from medpy.iterators import SlidingWindowIterator


@pytest.mark.parametrize(
    "size, expected_patches, expected_masks",
    [
        (1, [[1], [2], [3]], [[True], [True], [True]]),
        (2, [[-1, 1], [1, 2], [2, 3]], [[False, True], [True, True], [True, True]]),
        (
            3,
            [[-1, 1, 2], [1, 2, 3], [2, 3, -1]],
            [[False, True, True], [True, True, True], [True, True, False]],
        ),
        (
            5,
            [[-1, -1, 1, 2, 3], [-1, 1, 2, 3, -1], [1, 2, 3, -1, -1]],
            [
                [False, False, True, True, True],
                [False, True, True, True, False],
                [True, True, True, False, False],
            ],
        ),
    ],
)
def test_sliding_window_padding_and_mask(size, expected_patches, expected_masks):
    values = np.array([1, 2, 3])
    windows = SlidingWindowIterator(values, size, cval=-1)
    patches, masks, slicers = zip(*windows)

    np.testing.assert_array_equal(patches, expected_patches)
    np.testing.assert_array_equal(masks, expected_masks)
    for patch, slicer in zip(patches, slicers):
        np.testing.assert_array_equal(windows.applyslicer(values, slicer), patch)


@pytest.mark.parametrize("dtype", [np.uint8, np.uint16, np.uint32, np.uint64])
def test_sliding_window_accepts_unsigned_scalar_size(dtype):
    values = np.array([1, 2, 3])
    patches, masks, _ = zip(*SlidingWindowIterator(values, dtype(3), cval=-1))

    np.testing.assert_array_equal(patches, [[-1, 1, 2], [1, 2, 3], [2, 3, -1]])
    np.testing.assert_array_equal(
        masks, [[False, True, True], [True, True, True], [True, True, False]]
    )


def test_sliding_window_accepts_narrow_integer_sizes_on_long_axes():
    values = np.arange(600).reshape((300, 2))
    windows = list(SlidingWindowIterator(values, (np.int8(3), np.uint8(2))))
    assert len(windows) == values.size
    patch, mask, _ = windows[129 * values.shape[1] + 1]

    np.testing.assert_array_equal(patch, values[128:131, :])
    np.testing.assert_array_equal(mask, np.ones((3, 2), dtype=bool))


def test_sliding_window_with_empty_axis():
    values = np.empty((3, 0))
    windows = SlidingWindowIterator(values, (np.uint8(4), 3))

    assert list(windows) == []


@pytest.mark.parametrize("size", [0, (3, 0), (2, -1), (1, 2, 3)])
def test_sliding_window_rejects_bad_size(size):
    with pytest.raises(ValueError):
        SlidingWindowIterator(np.zeros((3, 2)), size)


def test_applyslicer_preserves_channels_and_fill_value():
    values = np.array([1, 2, 3])
    channels = np.stack((values, 10 * values), axis=-1)
    windows = SlidingWindowIterator(values, 3, cval=-1)
    _, _, slicer = next(windows)

    np.testing.assert_array_equal(
        windows.applyslicer(channels, slicer), [[-1, -1], [1, 10], [2, 20]]
    )
    np.testing.assert_array_equal(
        windows.applyslicer(channels, slicer, cval=0), [[0, 0], [1, 10], [2, 20]]
    )


def test_applyslicer_accepts_array_like():
    windows = SlidingWindowIterator([1, 2, 3], 3, cval=-1)
    _, _, slicer = next(windows)

    np.testing.assert_array_equal(windows.applyslicer([4, 5, 6], slicer), [-1, 4, 5])
