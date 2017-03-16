from __future__ import (absolute_import, division, print_function)
import unittest
import numpy.testing as npt
from tests import test_helper as th


class NormaliseByFlatDarkTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(NormaliseByFlatDarkTest, self).__init__(*args, **kwargs)

        # force silent outputs
        from configs.recon_config import ReconstructionConfig
        self.config = ReconstructionConfig.empty_init()
        self.config.func.verbosity = 0

        from filters import normalise_by_flat_dark
        self.alg = normalise_by_flat_dark

    def test_not_executed(self):
        images, control = th.gen_img_shared_array_and_copy()
        flat = th.gen_img_shared_array()[0]
        dark = th.gen_img_shared_array()[0]
        err_msg = "TEST NOT EXECUTED :: Running normalise_by_flat_dark with size {0}, mode {1} and order {2} changed the data!"

        # empty params
        result = self.alg.execute(images)
        npt.assert_equal(result, control)

        # no dark
        self.alg.execute(images, flat[0])
        th.assert_equals(images, control)
        # no flat
        self.alg.execute(images, None, dark[0])
        th.assert_equals(images, control)

        # bad flat
        npt.assert_raises(ValueError, self.alg.execute, images, flat[0], dark)
        # bad dark
        npt.assert_raises(ValueError, self.alg.execute, images, flat, dark[0])

    def test_executed_par(self):
        self.do_execute()

    def test_executed_seq(self):
        th.switch_mp_off()
        self.do_execute()
        th.switch_mp_on()

    def do_execute(self):
        images, control = th.gen_img_shared_array_and_copy()
        flat = th.gen_img_shared_array()[0]
        dark = th.gen_img_shared_array()[0]

        import numpy as np
        # making sure to not count on complete randomness
        images[0, 0, 0] = 2.5
        control[0, 0, 0] = 2.5
        result = self.alg.execute(images, flat, dark, 0, 1.5)
        th.assert_not_equals(images, control)

        control = np.full((10, 10, 10), 442.)
        result = self.alg.execute(images, flat, dark, 442., 442)
        npt.assert_equal(result, control)

        control = np.zeros(1000).reshape(10, 10, 10)
        result = self.alg.execute(images, flat, dark, 0, 0)
        npt.assert_equal(result, control)

    def test_real_result(self):
        th.switch_mp_off()
        self.do_execute()
        th.switch_mp_on()

    def do_real_result(self, helper):
        # the operation is (sample - dark) / (flat - dark)
        sample = th.gen_img_shared_array()
        sample[:] = 846.
        flat = th.gen_img_shared_array()[0]
        flat[:] = 26.
        dark = th.gen_img_shared_array()[0]
        dark[:] = 6.
        import numpy as np
        expected = np.full(sample.shape, 42.)

        # we dont want anything to be cropped out
        res = self.alg.execute(sample, flat, dark, 0, 1000)
        th.assert_equals(res, expected)


if __name__ == '__main__':
    unittest.main()
