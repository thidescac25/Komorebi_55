def get_currency_mapping():
    """
    Retourne un dictionnaire de mapping entre tickers et devises.
    À compléter avec toutes les 55 valeurs.
    """
    currency_mapping = {
        # Exemples (à compléter avec vos 55 valeurs)
        "GOOGL": "$",    # Dollar américain pour Alphabet
        "ERF.PA": "€",   # Euro pour Eurofins Scientific
        "GTT.PA": "€",   # Euro pour Gaztransport et Technigaz
        "GD": "$",       # Dollar américain pour General Dynamics
        "ROG.SW": "CHF", # Franc suisse pour Roche Holding
        "RR.L": "£",     # Livre sterling pour Rolls-Royce
        "UBSG.SW": "CHF", # Franc suisse pour UBS Group
        "VIE.PA": "€"    # Euro pour Veolia
        # Ajoutez le reste des 55 valeurs
    }
    return currency_mapping

# Rendements des dividendes par société (à compléter)
def get_dividend_yields():
    """
    Retourne un dictionnaire des rendements de dividendes manuels.
    À compléter avec toutes les 55 valeurs si nécessaire.
    """
    dividend_yields = {
        # Exemples (à compléter avec vos 55 valeurs si nécessaire)
        "GOOGL": 0.52,      # Alphabet
        "ERF.PA": 1.05,     # Eurofins Scientific
        "GTT.PA": 4.21,     # Gaztransport et Technigaz
        "GD": 2.01,         # General Dynamics
        "ROG.SW": 3.53,     # Roche Holding
        "RR.L": 1.17,       # Rolls-Royce
        "UBSG.SW": 1.82,    # UBS Group
        "VIE.PA": 4.41      # Veolia
        # Ajoutez le reste des 55 valeurs
    }
    return dividend_yields

# Fonction pour formatter les valeurs monétaires
def format_currency(value, currency="€"):
    """
    Formate une valeur monétaire avec le symbole de devise approprié.
    
    Args:
        value (float): Valeur à formater
        currency (str): Symbole de la devise ($, €, £, CHF, etc.)
        
    Returns:
        str: Valeur formatée avec devise
    """
    if currency in ["$", "€", "£"]:
        return f"{currency}{value:,.2f}"
    else:
        return f"{value:,.2f} {currency}"

# Fonction pour formatter les pourcentages
def format_percentage(value, include_sign=True):
    """
    Formate une valeur en pourcentage.
    
    Args:
        value (float): Valeur à formater
        include_sign (bool): Inclure le signe + pour les valeurs positives
        
    Returns:
        str: Valeur formatée en pourcentage
    """
    sign = "+" if value > 0 and include_sign else ""
    return f"{sign}{value:.2f}%"