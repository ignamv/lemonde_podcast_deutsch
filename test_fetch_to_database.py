"""Tests for fetch_to_database"""
import datetime
from fetch_to_database import parse_issue_html


def test_parse_issue():
    """."""
    input_ = """
<ul class="inhaltsverz verlinkt">
  <li mediasyncid="5812125">
    <div>
      <a href="/artikel/!5812125"> <strong>the title</strong> </a>
    </div>
    <div>summary</div>
    <div>
      <span><em> von </em></span><span><em>author1</em></span>, <span><em>author2</em></span>
    </div>
  </li>
</ul>"""
    date = datetime.date(1998, 12, 30)
    (summary,) = parse_issue_html(input_, date)
    assert summary.mediasyncid == 5812125
    assert summary.url == "/artikel/!5812125"
    assert summary.title == "the title"
    assert summary.summary == "summary"
    assert summary.authors == ["author1", "author2"]
    assert summary.date == date
