# coding=utf-8

class intentData():
    data = {
        "vente": {
            "examples" : [
                "Combien de sacs avons-nous vendu la semaine derniere",
                "quelle est la quantité de souliers vendus durant les 3 derniers jours",
                "pantalons vendus hier",
                "combien de sacs ont été vendus à montaigne le mois dernier",
                "manteaux vendus à des chinois pendant l'année dernière",
                "quantité de blousons écoulée au Japon",
                "quel mix de couleurs vend on sur a collection j'adior",
                "quelle est la couleur de chemise qui se vend le plus",
                "tailles de bague vendues à Sao Paulo",
                "montaigne vend combien de chemises",
                "prix moyen de vente du sac lady dior",
                "ecart-type du prix ttc du collier or",
                "prix de vente ht de la robe rouge baby",
                "Ce mois-ci, d'où venaient mes plus gros clients à New York",
                "Quelle est la nationalité des plus grands acheteurs de bagues",
                "Est-ce que la plupart des clients au Moyen Orient sont locaux",
                "Quel pourcentage des achats faits en Chine est fait par des chinois",
                "Quelle part de russes dans les achats de Lady Dior",
                "Les américains achètent-ils plus que les japonais",
                "Combien de ventes exceptionnelles",
                "Ai je eu des ventes exceptionnelles en souliers ce mois-ci",
                "Quelle croissance sur le japon"
            ]
        },"stock": {
            "examples" : [
                "Quel est le pourcentage du sellthru au Japon de la semaine dernière",
                "Quel est le pourcentage de sellthru en Asie de l'année dernière",
                "Quel est le nombre de points de sellthru de Madrid la semaine derniere en Lady Dior",
                "Quel est le sellthru de Paris le mois dernier",
                "Quel est le sellthru à paris en dior homme la semaine derniere"
                "Combien de points de sellthru en Asie le mois dernier"
                "quelle est la couverture de stock de Ginza en Lady Dior",
                "couverture de stock en joaillerie à paris",
                "quelle est ma couverture de stock à madrid pour l'article coccinnelle",
                "vestes restantes rue lapalce",
                "stock de roses des vents au Qatar",
                "combien de badges y a-t-il à new-york",
                "combien de montres ai-je en stock dans ma boutique",
                "stock restant de chemises en amerique",
                "Quelle est notre couverture moyenne de stocks en Sacs Femme?",
                "pins restant en boutique à shanghai",
                "converture de stock de la collection jadior",
                "stock de pantalons à londres",
                "taille de mon stock en amerique",
                "Quelle est la boutique en France avec la meilleure couverture de stocks",
            ]
        },"bonjour": {
            "examples" : ["bonjour",
                "hey",
                "hello",
                "Bonjour",
                "yo",
                "coucou !",
                "Salut !",
                "Comment ca va ?"
            ]
        },"boutique": {
            "examples" : [
                "ou se vend le mieux l'article 172h19h",
                "Où a-t-on écoulé le plus de souliers la semaine dernière",
                "A quel endroit a-t-on les meilleures ventes en J'Adior",
                "Où vent-on le plus de Lady Dior",
                "Qui sont les meilleures croissances du mois",
                "Quelles sont les meilleurs boutiques du mois",
                "J'aimerais connaître ma meilleure boutique ce mois-ci",
                "Quelles zone vend le plus de bags",
                "Ou avons nous vendu des crocos hier",
                "Ou sont partis les crocos",
                "Qui a vendu les crocos hier",
                "Où a été vendue la maro cette semaine",
                "Boutique vendant le plus aux Russes",
                "Quelles sont les meilleures boutiques en ventes de J'Adior",
                "Qui ont le plus vendu de Lady Dior",
                "Quelle est la boutique vendant le plus aux locaux ",
                "Dans quel pays vent-on le plus de roses des vents",
                "Dans quel pays les crocos s'écoulent-ils le mieux",
                "Donne-moi ma meilleure boutique du Japon",
                "Quelle boutique vend le plus de roses des vents",
            ]
        }, "vendeur": {
            "examples" : ["Qui est le meilleur vendeur",
                "Qui sont les dix meilleurs vendeurs",
                "Donne-moi le top 10 des vendeurs au Japon",
                "Qui est mon meilleur vendeur",
                "Je veux savoir qui est le meilleur vendeur",
                "Quel vendeur a fait la meilleure performance",
                "Quel vendeur vend le plus",
                "Les trois derniers jours, qui a été le meilleur vendeur en Russie",
                "Dis-moi qui a écoulé le plus de Roses des Vents",
                "Qui a vendu le plus de Lady Dior ce mois-ci à Paris",
                "Quel vendeur a vendu le plus de Lady Dior cette semaine à Tokyo",
                "Quel est le nom de celui qui vend le plus de souliers à Madrid",
                "Et qui vend le moins à Montaigne",
                "A Paris, qui vend le plus de sacs",
                "La semaine dernière, qui a conclu le plus de ventes à Ginza",
                "Aux Etats Unis, je veux mon vendeur le plus performant",
                "Combien de vendeurs y a-t-il à Montaigne",
                "Nombre de vendeurs au Moyen Orient"
            ]
        }
    }
    test = {
        "produit": {
            "examples" : [
                "Quelles sont les ventes de la semaine ?",
                "Quels sont les prochains pics de ventes à anticiper ?",
                "Comment cela se compare-t-il en valeur à l’année dernière, et l’année d’avant ?",
                "Quelle est la tendance au Japon ce mois-ci, au global, auprès des Clientèles Locales et des Clientèles Touristiques ?",
                "Quelles sont les Catégories s’étant le mieux vendu à Paris cette semaine ?",
                "Quel chiffre a été fait au Moyen-Orient, et quelle est la croissance au Moyen-Orient depuis le début d’année à taux constants ?",
                "Combien de Lady Dior ont été vendus cette semaine ?",
                "Cela représente quelle part des ventes en volume de la semaine ?",
                "Quels sont les volumes du MyLady ?",
                "Quelle est la deuxième ligne de sacs la mieux vendue cette semaine ?",
                "En PAP Femme, combien de points de Sell-Through ont été gagnés à date en volume sur la collection Croisière ?",
                "Combien le Japon a-t-il commandé de sacs J’Adior lors des achats en showroom?",
                "Comment se vend et progresse la Tribale ?",
                "Comment se vendent et progressent les Souliers ?",
                "Combien de Sacs Homme se sont vendus cette semaine ? (ventes et croissance)"
            ]
        },
        "boutique": {
            "examples" : [
                "Y a-t-il eu des Family Sales ou des Soldes ayant augmenté le chiffre ?",
                "Où en est la Gross Margin cette semaine, par rapport à l’année précédente et l’année d’avant?",
                "Quelle est la première boutique cette semaine ?",
                "Quel chiffre et quelle croissance ?",
                "Montaigne, Bond Street et Peking Road ont-elles une couverture moyenne de stocks en Sacs Femme supérieure à 3 mois ?",
                "Et en particulier sur les références les plus vendues à date de Lady Dior ?"
            ]
        },
        "nationalite": {
            "examples" : [
                "Quelles sont les Nationalités Clientes ayant le plus acheté à Paris cette semaine ?",
                "Avec quelles croissances vs. LY ?",
                "Quelle est la tendance sur les Clientèles locales cette semaine ?",
                "Quel est le poids des Clientèles Locales vs. Touristiques en Year To Date ?"
            ]
        },
        "vendeur": {
            "examples" : [

            ]
        },
    }
