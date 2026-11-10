# Data Crawler Configuration Template

# Python Crawler Settings
CRAWLER_CONFIG = {
    # Web crawling
    "seed_url": "https://example-intelligence.local",
    "max_pages": 12,
    "max_content_bytes": 1_800_000,  # 1.8 MB
    "max_depth": 3,
    "request_timeout": 20,
    "request_delay": 0.8,  # seconds between requests

    # Asset extraction
    "enable_image_extraction": True,
    "enable_pdf_extraction": True,
    "enable_archive_extraction": False,

    # GPS and location
    "gps_proximity_threshold_km": 1.0,  # Cluster radius
    "geohash_precision": 5,  # ~1.1m accuracy

    # Entity configuration
    "target_entities": [
        "PERSON_A",
        "PERSON_B",
        "LOCATION_X",
        "ASSET_ALPHA",
    ],

    # LLM Configuration (Ollama)
    "ollama_model": "dolphin-llama3",
    "ollama_url": "http://127.0.0.1:11434/api/generate",
    "ollama_timeout": 25,
    "ollama_temperature": 0.0,

    # Matching and Analysis
    "fuzzy_match_threshold": 75,  # 0-100
    "min_co_occurrence_docs": 2,
    "confidence_score_threshold": 0.35,  # Links below this are dropped

    # Storage and Output
    "output_format": "json",
    "export_knowledge_graph": True,
    "export_timeline": True,
    "export_location_heatmap": True,
}

# Database Configuration (Spring Boot)
DATABASE_CONFIG = {
    "spring": {
        "datasource": {
            "url": "jdbc:postgresql://localhost:5432/crawler_db",
            "username": "crawler_user",
            "password": "CHANGE_ME",
            "driver-class-name": "org.postgresql.Driver",
        },
        "jpa": {
            "hibernate": {
                "ddl-auto": "update",  # or "create" for fresh start
            },
            "properties": {
                "hibernate.dialect": "org.hibernate.dialect.PostgreSQL12Dialect",
                "hibernate.format_sql": True,
                "hibernate.jdbc.batch_size": 20,
                "hibernate.order_inserts": True,
                "hibernate.order_updates": True,
                "hibernate.envers.enabled": True,
                "hibernate.envers.audit_table_suffix": "_AUD",
                "hibernate.envers.revision_field_name": "rev",
                "hibernate.envers.revision_type_field_name": "revtype",
            },
        },
        "jpa.show-sql": False,
        "jpa.properties.hibernate.generate_statistics": False,
    },
    "server": {
        "port": 8080,
    },
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "detailed": {
            "format": "%(asctime)s [%(levelname)s] %(name)s - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "INFO",
            "formatter": "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/crawler.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "trawler_enhanced": {
            "level": "INFO",
            "handlers": ["console", "file"]
        },
        "metadata_extractor": {
            "level": "INFO",
            "handlers": ["console", "file"]
        },
        "analysis_engine": {
            "level": "INFO",
            "handlers": ["console", "file"]
        }
    }
}

# Performance Tuning
PERFORMANCE_CONFIG = {
    # Connection pooling
    "database_pool_size": 10,
    "database_max_idle_time": 300,

    # Caching
    "cache_enabled": True,
    "cache_ttl_seconds": 3600,
    "cache_max_size": 1000,

    # Batch processing
    "batch_size": 50,
    "thread_pool_size": 4,

    # Memory management
    "max_results_per_query": 10000,
    "streaming_threshold": 1000,
}

# Security Settings
SECURITY_CONFIG = {
    "verify_ssl": True,
    "allowed_domains": [
        "example-intelligence.local",
        "*.example.com",
    ],
    "max_redirects": 5,
    "user_agent": "EnhancedMemoryWebTrawler/2.0",
}

# Export Settings
EXPORT_CONFIG = {
    "formats": ["json", "csv", "graphml"],
    "output_directory": "./export",
    "include_metadata": True,
    "include_evidence": True,
    "compress_output": True,
    "timestamp_exports": True,
}

# Advanced Analysis Settings
ANALYSIS_CONFIG = {
    # Entity extraction
    "enable_nlp_extraction": False,  # Requires additional models
    "spacy_model": "en_core_web_sm",

    # Relationship strength calculation
    "weight_confidence": 0.6,
    "weight_frequency": 0.25,
    "weight_diversity": 0.15,

    # Timeline analysis
    "temporal_window_hours": 24,
    "timeline_resolution": "daily",

    # Anomaly detection
    "enable_anomaly_detection": False,
    "anomaly_std_devs": 2.0,

    # Clustering algorithms
    "clustering_algorithm": "kmeans",  # or "dbscan"
    "kmeans_clusters": 5,
    "dbscan_eps": 0.5,
}
