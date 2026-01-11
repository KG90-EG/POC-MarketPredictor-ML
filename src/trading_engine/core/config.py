"""
Centralized configuration management for the trading application.
Provides a single source of truth for all configurable parameters.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ModelConfig:
    """ML model configuration"""

    prod_model_path: str = field(
        default_factory=lambda: os.getenv("PROD_MODEL_PATH", "models/prod_model.bin")
    )
    feature_names: List[str] = field(
        default_factory=lambda: [
            "SMA50",
            "SMA200",
            "RSI",
            "Volatility",
            "Momentum_10d",
            "MACD",
            "MACD_signal",
            "BB_upper",
            "BB_lower",
        ]
    )


@dataclass
class APIConfig:
    """API and service configuration"""

    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )
    openai_model: str = field(
        default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    )
    rate_limit_rpm: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_RPM", "60"))
    )
    redis_url: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_URL"))
    mlflow_tracking_uri: str = field(
        default_factory=lambda: os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns")
    )
    s3_bucket: Optional[str] = field(default_factory=lambda: os.getenv("S3_BUCKET"))


@dataclass
class CacheConfig:
    """Cache TTL configuration"""

    ai_analysis_ttl: int = 300  # 5 minutes
    country_stocks_ttl: int = 3600  # 1 hour
    ticker_info_ttl: int = 1800  # 30 minutes
    ranking_ttl: int = 3600  # 1 hour


@dataclass
class SignalConfig:
    """Trading signal thresholds"""

    strong_buy_threshold: float = 0.65
    buy_threshold: float = 0.55
    hold_min_threshold: float = 0.45
    hold_max_threshold: float = 0.55
    consider_selling_threshold: float = 0.35

    def get_signal(self, probability: float) -> str:
        """Get trading signal based on probability"""
        if probability >= self.strong_buy_threshold:
            return "STRONG BUY"
        elif probability >= self.buy_threshold:
            return "BUY"
        elif probability >= self.hold_min_threshold:
            return "HOLD"
        elif probability >= self.consider_selling_threshold:
            return "CONSIDER SELLING"
        else:
            return "SELL"


@dataclass
class MarketConfig:
    """Market and stock configuration"""

    default_stocks: List[str] = field(
        default_factory=lambda: [
            # === US Stocks (30) ===
            # Tech Giants
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "NVDA",
            "META",
            "TSLA",
            "NFLX",
            "ADBE",
            "CRM",
            # Finance
            "JPM",
            "BAC",
            "WFC",
            "GS",
            "MS",
            "V",
            "MA",
            "PYPL",
            # Healthcare & Pharma
            "UNH",
            "JNJ",
            "PFE",
            "ABBV",
            # Consumer & Retail
            "WMT",
            "COST",
            "HD",
            "NKE",
            "MCD",
            # Energy & Industrial
            "XOM",
            "CVX",
            "BA",
            # === Swiss SMI Index (20) ===
            "NESN.SW",
            "NOVN.SW",
            "ROG.SW",
            "UBSG.SW",
            "ZURN.SW",
            "ABBN.SW",
            "CFR.SW",
            "LONN.SW",
            "SIKA.SW",
            "GIVN.SW",
            "SREN.SW",
            "GEBN.SW",
            "PGHN.SW",
            "SGSN.SW",
            "SCMN.SW",
            "HOLN.SW",
            "ALC.SW",
            "KNIN.SW",
            "UHR.SW",
            "ADEN.SW",
        ]
    )

    country_seeds: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "Switzerland": [
                "NESN.SW",
                "NOVN.SW",
                "ROG.SW",
                "UBSG.SW",
                "ZURN.SW",
                "ABBN.SW",
                "SREN.SW",
                "GIVN.SW",
                "LONN.SW",
                "SLHN.SW",
                "SCMN.SW",
                "ADEN.SW",
                "GEBN.SW",
                "PGHN.SW",
                "SGSN.SW",
                "CSGN.SW",
                "HOLN.SW",
                "CFR.SW",
                "SYNN.SW",
                "STMN.SW",
            ],
            "Germany": [
                # DAX 40 Index - Top 30
                "SAP.DE",
                "SIE.DE",
                "ALV.DE",
                "DTE.DE",
                "VOW3.DE",
                "MBG.DE",
                "BMW.DE",
                "BAS.DE",
                "ADS.DE",
                "MUV2.DE",
                "BAYN.DE",
                "EOAN.DE",
                "DB1.DE",
                "HEN3.DE",
                "IFX.DE",
                "RHM.DE",
                "DAI.DE",
                "FRE.DE",
                "SHL.DE",
                "BEI.DE",
                "RWE.DE",
                "LIN.DE",
                "ZAL.DE",
                "PUM.DE",
                "MRK.DE",
                "QIA.DE",
                "CON.DE",
                "1COV.DE",
                "PAH3.DE",
                "SRT3.DE",
            ],
            "UK": [
                # FTSE 100 - Top 20
                "SHEL.L",
                "AZN.L",
                "HSBA.L",
                "BP.L",
                "ULVR.L",
                "DGE.L",
                "GSK.L",
                "RIO.L",
                "BATS.L",
                "RELX.L",
                "NG.L",
                "LSEG.L",
                "VOD.L",
                "PRU.L",
                "BARC.L",
                "LLOY.L",
                "AAL.L",
                "GLEN.L",
                "IMB.L",
                "CRH.L",
            ],
            "France": [
                # CAC 40 - Top 20
                "MC.PA",
                "OR.PA",
                "SAN.PA",
                "TTE.PA",
                "AIR.PA",
                "SAF.PA",
                "BNP.PA",
                "AI.PA",
                "EL.PA",
                "SU.PA",
                "CS.PA",
                "DG.PA",
                "KER.PA",
                "VIE.PA",
                "CAP.PA",
                "RMS.PA",
                "EN.PA",
                "SGO.PA",
                "PUB.PA",
                "DSY.PA",
            ],
            "Japan": [
                "TM",
                "7203.T",
                "6758.T",
                "8306.T",
                "6861.T",
                "9984.T",
                "6902.T",
                "9432.T",
                "8035.T",
                "7974.T",
                "4063.T",
                "4502.T",
                "6501.T",
                "4503.T",
                "6954.T",
                "6098.T",
                "9433.T",
                "4568.T",
                "6273.T",
                "7267.T",
            ],
            "Canada": [
                "SHOP.TO",
                "TD.TO",
                "RY.TO",
                "BNS.TO",
                "ENB.TO",
                "CNR.TO",
                "CP.TO",
                "BMO.TO",
                "CNQ.TO",
                "TRP.TO",
                "CM.TO",
                "SU.TO",
                "WCN.TO",
                "MFC.TO",
                "BAM.TO",
                "ABX.TO",
                "BCE.TO",
                "FNV.TO",
                "QSR.TO",
                "NTR.TO",
            ],
        }
    )

    country_indices: Dict[str, str] = field(
        default_factory=lambda: {
            "Switzerland": "^SSMI",
            "Germany": "^GDAXI",
            "UK": "^FTSE",
            "France": "^FCHI",
            "Japan": "^N225",
            "Canada": "^GSPTSE",
        }
    )


@dataclass
class LoggingConfig:
    """Logging configuration"""

    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    log_format: str = "[%(asctime)s] [%(levelname)-8s] [%(request_id)s] %(message)s"


@dataclass
class AppConfig:
    """Main application configuration container"""

    model: ModelConfig = field(default_factory=ModelConfig)
    api: APIConfig = field(default_factory=APIConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    signal: SignalConfig = field(default_factory=SignalConfig)
    market: MarketConfig = field(default_factory=MarketConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @classmethod
    def load(cls) -> "AppConfig":
        """Load configuration from environment and defaults"""
        return cls()

    def validate(self) -> None:
        """Validate configuration and log warnings for missing optional settings"""
        from ..utils.logging_config import setup_logging

        logger = setup_logging(self.logging.log_level)

        if not self.api.openai_api_key:
            logger.warning(
                "OPENAI_API_KEY not set - AI analysis features will be unavailable"
            )

        if not self.api.redis_url:
            logger.info(
                "REDIS_URL not set - using in-memory cache (not shared across instances)"
            )

        if not os.path.exists(self.model.prod_model_path):
            logger.warning(f"Model file not found at {self.model.prod_model_path}")


# Global configuration instance
config = AppConfig.load()
