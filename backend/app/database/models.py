import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.session import Base

def utcnow():
    return datetime.datetime.now(datetime.timezone.utc)

class Competitor(Base):
    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    website_url = Column(String(512), nullable=False)
    blog_url = Column(String(512), nullable=True)
    feed_url = Column(String(512), nullable=True)
    sitemap_url = Column(String(512), nullable=True)
    monitoring_enabled = Column(Boolean, default=True, index=True)
    status = Column(String(50), default="active", index=True)  # active, paused, error, analyzing
    check_interval_sec = Column(Integer, default=60)
    last_checked = Column(DateTime(timezone=True), nullable=True)
    last_successful_detection = Column(DateTime(timezone=True), nullable=True)
    auto_discovered_config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    # Relationships
    sources = relationship("MonitoringSource", back_populates="competitor", cascade="all, delete-orphan", lazy="selectin")
    articles = relationship("Article", back_populates="competitor", cascade="all, delete-orphan", lazy="selectin")
    logs = relationship("MonitoringLog", back_populates="competitor", cascade="all, delete-orphan", lazy="selectin")


class MonitoringSource(Base):
    __tablename__ = "monitoring_sources"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # RSS, SITEMAP, DIRECT_PAGE
    source_url = Column(String(512), nullable=False)
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # 1 = Primary, 2 = Secondary, 3 = Fallback
    last_checked = Column(DateTime(timezone=True), nullable=True)
    last_status = Column(String(50), nullable=True)  # OK, ERROR, TIMEOUT
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)

    competitor = relationship("Competitor", back_populates="sources")


class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(512), nullable=False)
    url = Column(String(1024), nullable=False)
    canonical_url = Column(String(1024), unique=True, index=True, nullable=False)
    author = Column(String(255), nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True, index=True)
    detected_at = Column(DateTime(timezone=True), default=utcnow, index=True)
    detection_delay_seconds = Column(Float, nullable=True)  # Exact difference in seconds: detected_at - published_at
    detection_delay_formatted = Column(String(64), nullable=True)  # e.g., "3m 12s" or "47s"
    detection_method = Column(String(50), nullable=False)  # RSS, SITEMAP, DIRECT_PAGE
    content = Column(Text, nullable=True)
    featured_image = Column(String(1024), nullable=True)
    meta_description = Column(Text, nullable=True)
    categories = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    inline_images = Column(JSON, default=list)
    relevant_links = Column(JSON, default=list)
    raw_metadata = Column(JSON, default=dict)
    status = Column(String(50), default="detected")  # detected, processed, failed
    created_at = Column(DateTime(timezone=True), default=utcnow)

    competitor = relationship("Competitor", back_populates="articles")


class MonitoringLog(Base):
    __tablename__ = "monitoring_logs"

    id = Column(Integer, primary_key=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id", ondelete="CASCADE"), nullable=False, index=True)
    source_id = Column(Integer, nullable=True)
    checked_at = Column(DateTime(timezone=True), default=utcnow, index=True)
    status = Column(String(50), nullable=False)  # success, error, timeout, warning
    response_time_ms = Column(Float, default=0.0)
    articles_found = Column(Integer, default=0)
    new_articles_detected = Column(Integer, default=0)
    strategy_used = Column(String(50), nullable=False)  # RSS, SITEMAP, DIRECT_PAGE, MULTI
    error_message = Column(Text, nullable=True)

    competitor = relationship("Competitor", back_populates="logs")


class DemoArticle(Base):
    """Articles on the controlled demo testing site for interactive live tests"""
    __tablename__ = "demo_articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(512), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    content = Column(Text, nullable=False)
    author = Column(String(255), default="Demo Tech Editor")
    category = Column(String(100), default="AI & Cloud")
    featured_image = Column(String(1024), nullable=True)
    published_at = Column(DateTime(timezone=True), default=utcnow)
    is_published = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
