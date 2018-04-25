from tuttle.error import TuttleError
from tuttle.figures_formating import nice_size, nice_duration, parse_duration


class TestFileSizeFormating:

    def test_nice_size_B(self):
        """ A number below 1 000 B should be expressed in B"""
        nice = nice_size(12)
        assert nice == "12 B", nice

    def test_nice_size_KB(self):
        """ A number below 1 000 000 B should be expressed in KB"""
        nice = nice_size(12034)
        assert nice == "11.7 KB", nice

    def test_nice_size_MB(self):
        """ A number below 1 000 000 0000 B should be expressed in MB"""
        nice = nice_size(12056000)
        assert nice == "11.4 MB", nice

    def test_nice_size_MB_after_dot(self):
        """ A number below 1 000 000 0000 B should be expressed in MB"""
        nice = nice_size(12506000)
        assert nice == "11.9 MB", nice

    def test_nice_size_GB(self):
        """ A number below 1 000 000 0000 000 B should be expressed in GB"""
        nice = nice_size(12049000000)
        assert nice == "11.2 GB", nice


class TestDurationFormating:

    def test_nice_duration_s(self):
        """ A duration below the minute should be expressed in seconds"""
        nice = nice_duration(12)
        assert nice == "12s", nice

    def test_nice_duration_min(self):
        """ A duration below the hour should be expressed in minutes and seconds"""
        nice = nice_duration(64)
        assert nice == "1min 4s", nice

    def test_nice_size_hour(self):
        """ A duration below the day should be expressed in hours and minutes"""
        nice = nice_duration(10000)
        assert nice == "2h 46min", nice

    def test_nice_size_day(self):
        """ A duration above the day should be expressed in days and hours"""
        nice = nice_duration(1000000)
        assert nice == "11d 13h", nice


class TestDurationParsing:

    def test_parse_no_unit_is_seconds(self):
        """ When no unit is provided, the duration parser supposes it's seconds """
        d = parse_duration("12")
        assert d == 12, d

    def test_parse_negative_value(self):
        """ Should raise if the expression is negative because a duration can't be negative"""
        try:
            d = parse_duration("-1")
            assert False, "Should have raised"
        except ValueError as e:
            assert True

    def test_parse_seconds(self):
        """ should interpret s as seconds """
        d = parse_duration("12s")
        assert d == 12, d

    def test_parse_bad_expression(self):
        """ Should raise if the expression isn't a duration"""
        try:
            d = parse_duration("Not a number, Bro")
            assert False, "Should have raised"
        except ValueError as e:
            assert True

    def test_parse_minutes_secs(self):
        """ A duration can have minutes and seconds """
        d = parse_duration("14min 12s")
        assert d == 14*60 + 12, d

    def test_parse_minutes(self):
        """ A duration can have only minutes """
        d = parse_duration("14min")
        assert d == 14*60, d

    def test_parse_several_spaces(self):
        """ Figures and units also parts of the duration can be separated by any number of spaces """
        d = parse_duration("14  min     12 s")
        assert d == 14*60 + 12, d

    def test_parse_hours(self):
        """ A duration can have hours """
        d = parse_duration("3 h 12s")
        assert d == 3*3600 + 12, d

    def test_parse_days(self):
        """ A duration can have days """
        d = parse_duration("4d 12s")
        assert d == 4*24*3600 + 12, d
