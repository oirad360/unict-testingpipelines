# build on the top of Java image
FROM openjdk:16-jdk-alpine3.13
# JMeter Version
ARG JMETER_VERSION="5.6.2"
ENV JMETER_HOME /opt/apache-jmeter-${JMETER_VERSION}
ENV JMETER_LIB_FOLDER ${JMETER_HOME}/lib/

# Download and unpack the JMeter tar file
RUN cd /opt \
 && wget --no-check-certificate https://dlcdn.apache.org//jmeter/binaries/apache-jmeter-${JMETER_VERSION}.tgz \
 && tar xzf apache-jmeter-${JMETER_VERSION}.tgz \
 && rm apache-jmeter-${JMETER_VERSION}.tgz
# Create a symlink to the jmeter process in a normal bin directory
RUN ln -s /opt/apache-jmeter-${JMETER_VERSION}/bin/jmeter /usr/local/bin
# Copying postgres jdbc driver
WORKDIR ${JMETER_LIB_FOLDER}
RUN wget --no-check-certificate https://jdbc.postgresql.org/download/postgresql-42.2.24.jar 
# Add postgresql-client
RUN apk update && apk add --upgrade postgresql-client
WORKDIR ${JMETER_HOME}
