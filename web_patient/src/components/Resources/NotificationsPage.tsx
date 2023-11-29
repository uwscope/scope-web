import { Grid, Switch } from "@mui/material";
import { sub } from "date-fns";
import { del, get, set } from "idb-keyval";
import { action } from "mobx";
import { observer } from "mobx-react";
import React, { FunctionComponent, useEffect, useState } from "react";
import { useNavigate } from "react-router";
import { IPushSubscription } from "shared/types";
import { DetailPage } from "src/components/common/DetailPage";
import { getString } from "src/services/strings";
import { useStores } from "src/stores/stores";
import { urlB64ToUint8Array } from "src/utils/notifications";

export const NotificationsPage: FunctionComponent = observer(() => {
    const rootStore = useStores();
    const { patientStore } = rootStore;

    const navigate = useNavigate();

    const [enablePushNotification, setEnablePushNotification] = useState(false);

    const handleGoBack = action(() => {
        navigate(-1);
    });

    const switchHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (!!event.target.checked) {
            subscribePushNotification();
        } else {
            unsubscribePushNotification();
        }
    };

    // Verify if push notification is supported by the browser and disable or enable the toggle accordingly.
    const verifyDevicePushNotificationSupport = (): boolean => {
        if (!("serviceWorker" in navigator)) {
            console.info("Service Worker isn't supported on this browser.");
            // TODO: Show message in the UI.
            return true;
        }

        if (!("PushManager" in window)) {
            console.info("Push isn't supported on this browser.");
            // TODO: Show message in the UI.
            return true;
        }
        return false;
    };

    const subscribePushNotification = action(async () => {
        const result = await Notification.requestPermission();
        if (result === "denied") {
            // TODO: Figure out a neat way for the person to enable notifications in case they deny access during the first time the popup comes up.
            // Maybe show text in DOM asking them to allow notifications.
            // @link https://stackoverflow.com/questions/77209026/turning-on-notification-permission-on-pwa-after-permission-was-denied-in-app-set
            console.error("The user explicitly denied the permission request.");
            return;
        }
        if (result === "granted") {
            console.info("The user accepted the permission request.");
        }
        const registration = await navigator.serviceWorker.getRegistration();
        // TODO: What happens if registration is undefined. The push notification toggle can be disabled if service worker couldn't get regsitered.
        if (registration) {
            const subscribed = await registration.pushManager.getSubscription();
            if (subscribed) {
                // NOTE: We should never reach here as we unsubscribe the user when they toggle the switch to off.
                console.info("User is already subscribed.");
                // Check if the subscription is the same as the one in the IndexedDB.
                // TODO: Ensure idbSubscription is defined
                const idbSubscription = await get("subscription");
                console.assert(
                    idbSubscription.endpoint === subscribed.toJSON().endpoint,
                    "Subscription endpoint in IndexedDB and browser are different."
                );

                setEnablePushNotification(true);
                return subscribed;
            }

            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: urlB64ToUint8Array(
                    CLIENT_CONFIG.vapidPublicKey
                ),
            });
            console.info("Successfully subscribed to push notifications.");
            // Add subscription to database.
            const addedPushSubscription =
                await patientStore.addPushSubscription(
                    subscription.toJSON() as IPushSubscription
                );
            // Save subscription in IndexedDB.
            await set("subscription", addedPushSubscription);
            // Toggle the switch to on.
            setEnablePushNotification(true);
            return subscription;
        }
    });

    const unsubscribePushNotification = action(async () => {
        const registration = await navigator.serviceWorker.getRegistration();
        // TODO: What happens if registration is undefined. The push notification toggle can be disabled if service worker couldn't get registered.
        if (registration) {
            const subscribed = await registration.pushManager.getSubscription();
            if (subscribed) {
                // TODO: Ensure idbSubscription is defined
                const idbSubscription = await get("subscription");
                console.assert(
                    idbSubscription.endpoint === subscribed.toJSON().endpoint,
                    "Subscription endpoint in IndexedDB and browser are different."
                );

                const unsubscribed = await subscribed.unsubscribe();
                if (unsubscribed) {
                    console.info(
                        "Successfully unsubscribed from push notifications."
                    );
                    // Remove subscription from database.
                    patientStore.deletePushSubscription(
                        idbSubscription as IPushSubscription
                    );
                    // Remove subscription from IndexedDB.
                    del("subscription");
                    // Toggle the switch to off.
                    setEnablePushNotification(false);
                }
            }
        }
    });

    // Gets called on page load to get initial state of the push notification toggle.
    useEffect(() => {
        const checkDevicePushSubscription = action(async () => {
            const devicePushSubscription =
                await patientStore.checkDevicePushSubscription();

            setEnablePushNotification(!!devicePushSubscription);
        });
        checkDevicePushSubscription();
    }, []);

    return (
        <DetailPage
            title={getString("Resources_notifications_title")}
            onBack={handleGoBack}
        >
            <Grid
                container
                alignItems="center"
                spacing={1}
                justifyContent="center"
            >
                <Grid item>Allow Push Notification</Grid>
                <Grid item>
                    <Switch
                        checked={enablePushNotification}
                        color="primary"
                        onChange={switchHandler}
                        disabled={verifyDevicePushNotificationSupport()}
                        name="onOff"
                    />
                </Grid>
            </Grid>
        </DetailPage>
    );
});

export default NotificationsPage;
