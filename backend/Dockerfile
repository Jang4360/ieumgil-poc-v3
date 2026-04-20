FROM eclipse-temurin:21-jre-alpine AS runtime

WORKDIR /app

RUN apk add --no-cache wget

COPY build/libs/ieumgil-backend-*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-Xmx1g", "-Xms256m", "-Djava.security.egd=file:/dev/./urandom", "-jar", "app.jar"]
