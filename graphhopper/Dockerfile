FROM eclipse-temurin:21-jre-alpine

WORKDIR /graphhopper

RUN apk add --no-cache curl wget

ARG GH_VERSION=9.1
RUN wget -q "https://github.com/graphhopper/graphhopper/releases/download/${GH_VERSION}/graphhopper-web-${GH_VERSION}.jar" \
    -O graphhopper.jar

EXPOSE 8989

ENTRYPOINT ["java", "-Xmx4g", "-Xms1g", "-Ddw.server.application_connectors[0].port=8989", "-jar", "graphhopper.jar", "server", "/config/config.yaml"]
