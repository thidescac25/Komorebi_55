import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import datetime

@st.cache_data
def load_portfolio_data():
    """Chargement des données du portefeuille."""
    df = pd.read_csv("data/Portefeuille_55_business_models.csv")
    return df

@st.cache_data(ttl=60) 
def get_stock_data(ticker, detailed=False):
    """
    Récupère les données récentes d'une action.
    
    Arguments:
        ticker (str): Symbole de l'action
        detailed (bool): Si True, récupère des données plus détaillées
        
    Returns:
        dict: Dictionnaire contenant les données de l'action
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Données actuelles
        current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
        previous_close = info.get('previousClose', info.get('regularMarketPreviousClose', 0))
        change = current_price - previous_close
        percent_change = (change / previous_close) * 100 if previous_close else 0
        
        result = {
            'current_price': current_price,
            'previous_close': previous_close,
            'change': change,
            'percent_change': percent_change
        }
        
        if detailed:
            # Données financières
            sector = info.get('sector', "Non disponible")
            industry = info.get('industry', "Non disponible")
            country = info.get('country', "USA") 
            
            # Métriques financières
            pe_ratio = info.get('trailingPE', 0)
            dividend_yield = info.get('dividendYield', 0)
            
            # Performance annuelle (YTD)
            history = stock.history(period="ytd")
            if not history.empty:
                ytd_start = history.iloc[0]['Close']
                ytd_current = history.iloc[-1]['Close']
                ytd_change = ((ytd_current - ytd_start) / ytd_start) * 100
            else:
                ytd_change = 0
            
            # BPA
            eps = info.get('trailingEps', 0)
            market_cap = info.get('marketCap', 0) / 1_000_000_000 
            
            # Historique des prix pour le graphique
            hist = stock.history(period="1y")
            
            # Ajouter les données détaillées
            result.update({
                'sector': sector,
                'industry': industry,
                'country': country,
                'pe_ratio': pe_ratio,
                'dividend_yield': dividend_yield,
                'ytd_change': ytd_change,
                'eps': eps,
                'market_cap': market_cap,
                'history': hist
            })
            
        return result
    except Exception as e:
        # Gestion d'erreur simplifiée
        st.warning(f"Erreur lors de la récupération des données pour {ticker}: {e}")
        
        # Retourner un structure minimale mais valide
        result = {
            'current_price': 0,
            'previous_close': 0,
            'change': 0,
            'percent_change': 0
        }
        
        if detailed:
            result.update({
                'sector': "Non disponible",
                'industry': "Non disponible",
                'country': "Non disponible",
                'pe_ratio': 0,
                'dividend_yield': 0,
                'ytd_change': 0,
                'eps': 0,
                'market_cap': 0,
                'history': pd.DataFrame()
            })
            
        return result

@st.cache_data(ttl=3600)  # Cache pour 1 heure
def get_historical_data(tickers, start_date=None, end_date=None):
    """
    Récupère les données historiques pour une liste de tickers.
    
    Arguments:
        tickers (list): Liste des symboles d'actions
        start_date (datetime, optional): Date de début
        end_date (datetime, optional): Date de fin
        
    Returns:
        dict: Dictionnaire de DataFrames avec historique des prix
    """
    # Si end_date n'est pas fourni, utiliser la date actuelle
    if end_date is None:
        end_date = datetime.now()
        
    data = {}
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(start=start_date, end=end_date)
            if not hist.empty:
                # Pour éviter les problèmes de fuseau horaire, rendons les dates "naïves"
                hist.index = hist.index.tz_localize(None)
                data[ticker] = hist
            else:
                data[ticker] = pd.DataFrame()
        except Exception as e:
            st.warning(f"Erreur lors de la récupération des données pour {ticker}: {e}")
            data[ticker] = pd.DataFrame()
    return data

@st.cache_data(ttl=3600)  # Cache pour 1 heure
def load_sector_country_data(tickers):
    """
    Récupère secteur et pays pour chaque ticker via yfinance.
    
    Arguments:
        tickers (list): Liste des symboles d'actions
        
    Returns:
        DataFrame: DataFrame avec secteur et pays pour chaque ticker
    """
    data = []
    for tk in tickers:
        try:
            info = yf.Ticker(tk).info
            data.append({
                "Ticker": tk,
                "Sector": info.get("sector", "Non disponible"),
                "Country": info.get("country", "Non disponible")
            })
        except Exception as e:
            st.warning(f"Erreur lors de la récupération des données pour {tk}: {e}")
            data.append({
                "Ticker": tk,
                "Sector": "Non disponible",
                "Country": "Non disponible"
            })
    return pd.DataFrame(data)

@st.cache_data(ttl=3600)  # Cache pour 1 heure
def load_metrics(tickers):
    """
    Charge les métriques détaillées pour une liste de tickers.
    
    Arguments:
        tickers (list): Liste des symboles d'actions
        
    Returns:
        DataFrame: DataFrame avec les métriques pour chaque ticker
    """
    rows = []
    
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            
            # helpers
            def txt(k): return info.get(k, None)
            def num(k):
                v = info.get(k, None)
                return float(v) if v is not None else None
            
            rows.append({
                "Ticker":           ticker,
                "Nom complet":      txt("longName"),
                "Pays":             txt("country"),
                "Secteur":          txt("sector"),
                "Industrie":        txt("industry"),
                "Exchange":         txt("exchange"),
                "Devise":           txt("currency"),
                "Prix Actuel":      num("currentPrice"),
                "Clôture Prec.":    num("previousClose"),
                "52-sem. Bas":      num("fiftyTwoWeekLow"),
                "52-sem. Haut":     num("fiftyTwoWeekHigh"),
                "Moyenne 50j":      num("fiftyDayAverage"),
                "Moyenne 200j":     num("twoHundredDayAverage"),
                "Market Cap":       num("marketCap"),
                "PER (TTM)":        num("trailingPE"),
                "Div Yield":        num("dividendYield"),
                "Reco Analyses":    txt("recommendationKey"),
            })
        except Exception as e:
            st.warning(f"Erreur lors de la récupération des métriques pour {ticker}: {e}")
            rows.append({
                "Ticker":           ticker,
                "Nom complet":      "Non disponible",
                "Pays":             None,
                "Secteur":          None,
                "Industrie":        None,
                "Exchange":         None,
                "Devise":           None,
                "Prix Actuel":      None,
                "Clôture Prec.":    None,
                "52-sem. Bas":      None,
                "52-sem. Haut":     None,
                "Moyenne 50j":      None,
                "Moyenne 200j":     None,
                "Market Cap":       None,
                "PER (TTM)":        None,
                "Div Yield":        None,
                "Reco Analyses":    None,
            })
    
    dfm = pd.DataFrame(rows).set_index("Ticker")
    return dfm