package com.hotel.booking.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.sns.SnsClient;

@Configuration
public class AwsConfig {

    private static final Logger log = LoggerFactory.getLogger(AwsConfig.class);

    @Value("${aws.region:us-east-1}")
    private String awsRegion;

    @Bean
    public SnsClient snsClient() {
        try {
            return SnsClient.builder()
                    .region(Region.of(awsRegion))
                    .credentialsProvider(DefaultCredentialsProvider.create())
                    .build();
        } catch (Exception e) {
            log.warn("Không thể khởi tạo SnsClient với default credentials (có thể đang chạy offline/local mà chưa cấu hình AWS): {}", e.getMessage());
            return SnsClient.builder()
                    .region(Region.of(awsRegion))
                    .build();
        }
    }

    @Bean
    public DynamoDbClient dynamoDbClient() {
        try {
            return DynamoDbClient.builder()
                    .region(Region.of(awsRegion))
                    .credentialsProvider(DefaultCredentialsProvider.create())
                    .build();
        } catch (Exception e) {
            log.warn("Không thể khởi tạo DynamoDbClient với default credentials: {}", e.getMessage());
            return DynamoDbClient.builder()
                    .region(Region.of(awsRegion))
                    .build();
        }
    }
}
