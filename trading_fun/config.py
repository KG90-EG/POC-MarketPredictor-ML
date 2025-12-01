"""
Centralized configuration management for the trading application.
Provides a single source of truth for all configurable parameters.
"""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class ModelConfig:
    """ML model configuration"""

    prod_model_path: str = field(default_factory=lambda: os.getenv("PROD_MODEL_PATH", "models/prod_model.bin"))
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

    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    rate_limit_rpm: int = field(default_factory=lambda: int(os.getenv("RATE_LIMIT_RPM", "60")))
    redis_url: Optional[str] = field(default_factory=lambda: os.getenv("REDIS_URL"))
    mlflow_tracking_uri: str = field(default_factory=lambda: os.getenv("MLFLOW_TRACKING_URI", "file:./mlruns"))
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
            "AAPL",
            "MSFT",
            "GOOGL",
            "AMZN",
            "NVDA",
            "META",
            "TSLA",
            "BRK.B",
            "UNH",
            "JNJ",
            "V",
            "WMT",
            "JPM",
            "MA",
            "PG",
            "XOM",
            "HD",
            "CVX",
            "LLY",
            "ABBV",
            "MRK",
            "KO",
            "PEP",
            "COST",
            "AVGO",
            "TMO",
            "BAC",
            "CSCO",
            "MCD",
            "ACN",
            "AMD",
            "NFLX",
            "ADBE",
            "DIS",
            "NKE",
            "INTC",
            "CRM",
            "TXN",
            "ORCL",
            "ABT",
            "CMCSA",
            "VZ",
            "WFC",
            "PM",
            "IBM",
            "QCOM",
            "UPS",
            "HON",
            "BA",
            "GE",
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
                "KNIN.SW",
                "BALN.SW",
                "BUCN.SW",
                "LISN.SW",
                "VACN.SW",
                "BEAN.SW",
                "AREN.SW",
                "DUFN.SW",
                "TEMN.SW",
            ],
            "Germany": [
                "SAP",
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
                "CON.DE",
                "BEI.DE",
                "VNA.DE",
                "SAP.DE",
                "P911.DE",
                "HNR1.DE",
            ],
            "United Kingdom": [
                "SHEL.L",
                "AZN.L",
                "HSBA.L",
                "ULVR.L",
                "DGE.L",
                "BP.L",
                "GSK.L",
                "RIO.L",
                "LSEG.L",
                "NG.L",
                "REL.L",
                "BARC.L",
                "LLOY.L",
                "VOD.L",
                "PRU.L",
                "BT-A.L",
                "BATS.L",
                "AAL.L",
                "CRH.L",
                "IMB.L",
            ],
            "France": [
                "MC.PA",
                "OR.PA",
                "SAN.PA",
                "TTE.PA",
                "AIR.PA",
                "BNP.PA",
                "SU.PA",
                "AI.PA",
                "CA.PA",
                "EN.PA",
                "SGO.PA",
                "DG.PA",
                "CS.PA",
                "BN.PA",
                "KER.PA",
                "RMS.PA",
                "EL.PA",
                "CAP.PA",
                "VIV.PA",
                "ORA.PA",
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
            "United Kingdom": "^FTSE",
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
        from .logging_config import setup_logging

        logger = setup_logging(self.logging.log_level)

        if not self.api.openai_api_key:
            logger.warning("OPENAI_API_KEY not set - AI analysis features will be unavailable")

        if not self.api.redis_url:
            logger.info("REDIS_URL not set - using in-memory cache (not shared across instances)")

        if not os.path.exists(self.model.prod_model_path):
            logger.warning(f"Model file not found at {self.model.prod_model_path}")


# Global configuration instance
config = AppConfig.load()
