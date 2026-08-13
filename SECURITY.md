# Politique de sécurité

## Versions supportées

`django-signals-all` est en pré-version `1.0.0rc1` : seule la dernière
version publiée reçoit des correctifs de sécurité.

| Version    | Supportée |
| ---------- | --------- |
| 1.0.0rcN   | ✅        |
| < 1.0.0rc1 | ❌        |

## Signaler une vulnérabilité

Merci de **ne pas** ouvrir d'issue publique pour une faille de sécurité.

Le module `django_signals_all.sql` analyse du SQL potentiellement contrôlé
par des chemins applicatifs sensibles : toute faille permettant de
contourner `EXCLUDED_TABLES`/`MONITORED_TABLES`, de provoquer un déni de
service via le parsing, ou d'exécuter du code via un receiver mal isolé,
est considérée comme une vulnérabilité de sécurité.

Privilégiez le signalement privé via
[GitHub Security Advisories](https://github.com/alzeph/django-signals-all/security/advisories/new)
sur ce dépôt. À défaut, contactez l'auteur directement à
hervecedricyouan@gmail.com.

Merci d'inclure :

- une description du problème et de son impact potentiel ;
- les étapes pour le reproduire ;
- la version de `django-signals-all`, de Django et le SGBD concernés.

Nous accusons réception sous 72h et visons un correctif ou une réponse
motivée sous 30 jours selon la gravité.
