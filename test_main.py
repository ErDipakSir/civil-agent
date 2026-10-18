from main import Beam, Column, Slab, analyze


def test_beam_formulas():
    b = Beam("B1", 6, 0.3, 0.5, 10)
    assert round(b.volume(), 3) == 0.900
    assert round(b.weight(), 2) == 22.50
    assert round(b.bending_moment(), 2) == 45.00
    assert round(b.shear_force(), 2) == 30.00


def test_column_and_slab_volume():
    assert round(Column("C1", 0.3, 0.3, 3).volume(), 3) == 0.270
    assert round(Slab("S1", 6, 4, 0.15).volume(), 3) == 3.600


def test_analysis_totals():
    elements = [Beam("B1", 6, 0.3, 0.5, 10),
                Column("C1", 0.3, 0.3, 3),
                Slab("S1", 6, 4, 0.15)]
    lines = analyze(elements)
    assert "Total volume: 4.770 m3" in lines
    assert "Total weight: 119.25 kN" in lines