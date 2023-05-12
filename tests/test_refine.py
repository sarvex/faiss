# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import numpy as np
import unittest
import faiss

from faiss.contrib import datasets


class TestDistanceComputer(unittest.TestCase):

    def do_test(self, factory_string, metric_type=faiss.METRIC_L2):
        ds = datasets.SyntheticDataset(32, 1000, 200, 20)

        index = faiss.index_factory(32, factory_string, metric_type)
        index.train(ds.get_train())
        index.add(ds.get_database())
        xq = ds.get_queries()
        Dref, Iref = index.search(xq, 10)

        for is_FlatCodesDistanceComputer in False, True:
            if not is_FlatCodesDistanceComputer:
                dc = index.get_distance_computer()
            elif isinstance(index, faiss.IndexFlatCodes):
                dc = index.get_FlatCodesDistanceComputer()
            else:
                continue
            self.assertTrue(dc.this.own())
            for q in range(ds.nq):
                dc.set_query(faiss.swig_ptr(xq[q]))
                for j in range(10):
                    ref_dis = Dref[q, j]
                    new_dis = dc(int(Iref[q, j]))
                    np.testing.assert_almost_equal(
                        new_dis, ref_dis, decimal=5)

    def test_distance_computer_PQ(self):
        self.do_test("PQ8np")

    def test_distance_computer_SQ(self):
        self.do_test("SQ8")

    def test_distance_computer_SQ6(self):
        self.do_test("SQ6")

    def test_distance_computer_PQbit6(self):
        self.do_test("PQ8x6np")

    def test_distance_computer_PQbit6_ip(self):
        self.do_test("PQ8x6np", faiss.METRIC_INNER_PRODUCT)

    def test_distance_computer_VT(self):
        self.do_test("PCA20,SQ8")

    def test_distance_computer_AQ_decompress(self):
        self.do_test("RQ3x4")    # test decompress path

    def test_distance_computer_AQ_LUT(self):
        self.do_test("RQ3x4_Nqint8")    # test LUT path

    def test_distance_computer_AQ_LUT_IP(self):
        self.do_test("RQ3x4_Nqint8", faiss.METRIC_INNER_PRODUCT)
