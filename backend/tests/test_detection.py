import pytest
import datetime
from app.monitors.timing_engine import calculate_detection_delay, format_delay, compute_sla_metrics, normalize_datetime
from app.analyzers.blog_detector import BlogDetector

def test_timing_engine_calculation():
    now = datetime.datetime.now(datetime.timezone.utc)
    
    # 47 seconds delay
    pub_47s = now - datetime.timedelta(seconds=47)
    delay_sec, delay_fmt = calculate_detection_delay(pub_47s, now)
    assert round(delay_sec) == 47
    assert delay_fmt == "47s"

    # 3m 12s delay
    pub_3m12s = now - datetime.timedelta(minutes=3, seconds=12)
    delay_sec, delay_fmt = calculate_detection_delay(pub_3m12s, now)
    assert round(delay_sec) == 192
    assert delay_fmt == "3m 12s"

    # 1h 20m 00s delay
    pub_1h20m = now - datetime.timedelta(hours=1, minutes=20)
    delay_sec, delay_fmt = calculate_detection_delay(pub_1h20m, now)
    assert round(delay_sec) == 4800
    assert delay_fmt == "1h 20m"

def test_sla_metrics_computation():
    delays = [45, 120, 180, 290, 360, 600]  # 4 within 300s (5min), 2 over
    metrics = compute_sla_metrics(delays, target_seconds=300)
    
    assert metrics["total_articles"] == 6
    assert metrics["within_sla_count"] == 4
    assert metrics["over_sla_count"] == 2
    assert metrics["within_sla_percent"] == 66.7
    assert metrics["fastest_delay_seconds"] == 45
    assert metrics["slowest_delay_seconds"] == 600

def test_blog_detector_article_extraction():
    html = """
    <html>
        <body>
            <article class="post-card">
                <a href="/blog/ai-breakthrough-2026">AI Breakthrough in 2026</a>
            </article>
            <div class="article-item">
                <a href="/blog/distributed-systems-at-scale">Distributed Systems at Scale</a>
            </div>
            <a href="/category/tech">Category Tech</a>
        </body>
    </html>
    """
    links, meta = BlogDetector.extract_article_links("https://example.com/blog", html)
    assert len(links) >= 2
    assert any("ai-breakthrough-2026" in l for l in links)
    assert any("distributed-systems-at-scale" in l for l in links)
    # Ensure category link was excluded
    assert not any("/category/" in l for l in links)
