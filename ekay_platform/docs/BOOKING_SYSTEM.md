# Système de Réservation E-KAY

## Fonctionnalités

Le système de réservation permet aux utilisateurs de :
- Réserver des propriétés pour des dates spécifiques
- Voir l'historique de leurs réservations
- Gérer les réservations reçues (pour les propriétaires)
- Recevoir des notifications par email

## Modèles

### Booking
- `id` : Identifiant unique
- `property_id` : Référence à la propriété réservée
- `user_id` : Référence à l'utilisateur qui a effectué la réservation
- `start_date` : Date d'arrivée
- `end_date` : Date de départ
- `guests` : Nombre de voyageurs
- `status` : Statut de la réservation (pending/confirmed/cancelled/completed)
- `notes` : Notes ou demandes spéciales
- `created_at` : Date de création
- `updated_at` : Date de mise à jour

## Routes

### Réservation
- `GET|POST /property/<int:property_id>/book` : Formulaire et traitement de réservation
- `GET /booking/<int:booking_id>` : Détails d'une réservation
- `GET /my-bookings` : Liste des réservations de l'utilisateur
- `GET /host/bookings` : Liste des réservations reçues (pour les propriétaires)
- `POST /booking/<int:booking_id>/update-status` : Mise à jour du statut d'une réservation

## Emails

Le système envoie les emails suivants :
1. **Confirmation de réservation** : Envoyé au voyageur après une demande de réservation
2. **Notification de réservation** : Envoyé au propriétaire pour une nouvelle demande
3. **Confirmation de statut** : Envoyé lorsque le statut d'une réservation change
4. **Annulation** : Envoyé lorsqu'une réservation est annulée

## Sécurité

- Seuls les utilisateurs connectés peuvent effectuer des réservations
- Les utilisateurs ne peuvent voir que leurs propres réservations
- Les propriétaires ne peuvent modifier que les réservations de leurs propriétés
- Validation des dates pour éviter les réservations dans le passé

## Tests

Pour tester le système de réservation :

1. Connectez-vous en tant qu'utilisateur
2. Accédez à une propriété disponible
3. Cliquez sur "Réserver"
4. Remplissez le formulaire de réservation
5. Vérifiez que l'email de confirmation est reçu
6. Vérifiez que la réservation apparaît dans "Mes réservations"

## Améliorations futures

- Paiement en ligne intégré
- Système de notation et d'avis
- Calendrier de disponibilité en temps réel
- Notifications push
- Système de messagerie intégré
