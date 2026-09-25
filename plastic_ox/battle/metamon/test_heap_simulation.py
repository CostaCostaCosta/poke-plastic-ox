import unittest
from simulate_heap import Heap, replay


class HeapTests(unittest.TestCase):
    def test_alignment_and_small_tail(self):
        h = Heap(0x2000000, 128)
        p = h.alloc(81)
        self.assertEqual(p, 0x2000010)
        self.assertEqual(h.stats()['allocated'], 112)  # 28-byte tail cannot split.
        self.assertEqual(h.alloc(4), 0)
        h.free(p)
        self.assertEqual(h.stats()['free'], 112)

    def test_fragmentation_and_coalescing(self):
        h = Heap(0x2000000, 1024)
        a, b, c = [h.alloc(128) for _ in range(3)]
        d = h.alloc(h.stats()['largest'])
        h.free(a); h.free(c)
        self.assertEqual(h.stats()['free'], 256)
        self.assertEqual(h.alloc(200), 0)
        h.free(b)
        self.assertEqual(h.stats()['largest'], 416)
        h.free(d)
        self.assertEqual(h.stats()['free'], 1008)

    def test_double_free_detected(self):
        h = Heap(0x2000000, 128)
        p = h.alloc(16); h.free(p)
        with self.assertRaises(AssertionError): h.free(p)

    def trace(self):
        h = Heap(0x2000000, 65536)
        a = h.alloc(1000)
        h.free(a)
        rows = [(0, 0x2000000, 65536, 0), (3, 8, 0, 1),
                (1, a, 1000, 2), (3, 8, 0, 6), (3, 8, 0, 7),
                (3, 8, 0, 12), (3, 8, 0, 8), (2, a, 0, 8), (3, 8, 0, 9)]
        return dict(status='passed', heap_bytes=65536, locations={}, final_layout=h.layout(),
            events=[dict(kind=k, address=p, size=s, phase=ph, sequence=i, scenario='fixture', location=0)
                    for i, (k,p,s,ph) in enumerate(rows)])

    def test_baseline_and_relocated_policies(self):
        t = self.trace()
        for policy in ('baseline', 'resident', 'transient', 'menu-overlap'):
            r = replay(t, policy)
            self.assertTrue(r['viable_on_trace'], r)

    def test_pointer_drift_and_final_heap_are_detected(self):
        t = self.trace(); t['events'][2]['address'] += 4
        with self.assertRaisesRegex(AssertionError, 'pointer mismatch'): replay(t)
        t = self.trace(); t['final_layout'][0]['size'] -= 4
        with self.assertRaisesRegex(AssertionError, 'Final heap'): replay(t)

    def test_first_capacity_failure_is_reported(self):
        t = self.trace()
        r = replay(t, 'resident', history=64000)
        self.assertFalse(r['viable_on_trace'])
        self.assertEqual(r['first_failure']['owner'], 'model-persistent')

    def test_missing_end_marker_does_not_silently_leak(self):
        t = self.trace(); t['events'] = t['events'][:6]
        with self.assertRaisesRegex(AssertionError, 'leaked'): replay(t, 'menu-overlap')


if __name__ == '__main__': unittest.main()
