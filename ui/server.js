/* eslint-disable no-console */
import 'newrelic';  // must be first

import path from 'path';

import cfenv from 'cfenv';
import express from 'express';
import helmet from 'helmet';
import morgan from 'morgan';
import passport from 'passport';

import setupAuth from './auth';
import doNotCache from './do-not-cache';
import errorHandler from './error-handling';
import serverRender from './server-render';

const app = express();
const env = cfenv.getAppEnv();

setupAuth(env.getServiceCreds('config') || {});

/* Middleware */
// security headers. See docs around setOnOldIE: moral of the story is that
// ZAP masquerades as IE6 which triggers a different policy within helmet
app.use(helmet({ xssFilter: { setOnOldIE: true } }));
app.use(doNotCache);
// logging
app.use(morgan('combined'));
app.use('/static', express.static(path.join('ui-dist', 'static')));
app.use(passport.initialize());

app.get('*', passport.authenticate(['ip', 'basic'], { session: false }), serverRender);

// Error handler must be after all middleware and handlers
app.use(errorHandler);

/* Start */
app.listen(env.port, () => {
  console.log(`Listening on ${env.port}`);
});
