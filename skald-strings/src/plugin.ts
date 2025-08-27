import streamDeck, { LogLevel } from "@elgato/streamdeck";

import { IncrementCounter } from "./actions/increment-counter";

// We can enable "trace" logging so that all messages between the Stream Deck, and the plugin are recorded. When storing sensitive information
streamDeck.logger.setLevel(LogLevel.TRACE);

// Register the increment action.
streamDeck.actions.registerAction(new IncrementCounter());

streamDeck.system.onDidReceiveDeepLink((ev) => {
    streamDeck.logger.setLevel(LogLevel.TRACE);
	const { path, fragment } = ev.url;
	streamDeck.logger.info(`Path = ${path}`);
	streamDeck.logger.info(`Fragment = ${fragment}`);
    streamDeck.settings.setGlobalSettings({path});
});

streamDeck.logger.warn(streamDeck.settings.getGlobalSettings());

// Finally, connect to the Stream Deck.
streamDeck.connect();
