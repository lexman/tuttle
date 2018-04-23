from tuttle.figures_formating import nice_size, nice_duration


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