#ifndef ALERT_H
#define ALERT_H

void initAlert();
void setLED(bool green, bool yellow, bool red);
void buzzerWarning();
void buzzerLock();
void buzzerOff();

#endif