package ru.vyatsu.parser.otzovik;

import com.google.gson.stream.JsonWriter;
import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.select.Elements;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.FileWriter;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class OtzovikParser {
    private static final Logger logger = LoggerFactory.getLogger(OtzovikParser.class);
    private static final String url = "https://otzovik.com/show_filter.php?cat_id=117&order=date_desc&f[r]=%d_&page=%d";
    private static final String userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70";

    public static void parse(int moviesCount, final int reviewsPerMovie, final int minimumReviewsPerMovie,
                             final String outputPath) throws IOException {
        final Map<String, String> headers = new HashMap<>(
            Map.of("accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-encoding", "gzip, deflate, br",
                "accept-language", "en-US,en;q=0.9",
                "cache-control", "max-age=0",
                "cookie", "ssid=978101471; refreg=1647354570~https%3A%2F%2Fyandex.ru%2F; pr_form=advanced; yec=1; ROBINBOBIN=177edddac4254589980bf6b3b5; lastmenu=1",
                "referer", String.format("https://otzovik.com/show_filter.php?cat_id=117&order=date_desc&f[r]=%d_&page=", minimumReviewsPerMovie)
            ));
        headers.putAll(Map.of(
            "sec-ch-ua", "\"Opera GX\";v=\"83\", \"Chromium\";v=\"97\", \";Not A Brand\";v=\"99\"",
            "sec-ch-ua-mobile", "?0",
            "sec-ch-ua-platform", "Windows",
            "sec-fetch-dest", "document",
            "sec-fetch-mode", "navigate",
            "sec-fetch-site", "same-origin",
            "sec-fetch-user", "?1",
            "upgrade-insecure-requests", "1",
            "user-agent", userAgent
        ));

        JsonWriter jsonWriter = null;
        try {
            jsonWriter = new JsonWriter(new FileWriter(outputPath));
            jsonWriter.beginArray();
            logger.debug("Парсинг стартовал");
            for (int page = 1; moviesCount > 0; ++page) {
                final String referer = headers.get("referer");
                headers.put("referer", referer.substring(referer.lastIndexOf('=') + 1) + page);
                final Document doc = Jsoup.connect(String.format(url, minimumReviewsPerMovie, page))
                    .timeout(5000)
                    .userAgent(userAgent)
                    .ignoreContentType(true)
                    .ignoreHttpErrors(true)
                    .method(Connection.Method.GET)
                    .maxBodySize(Integer.MAX_VALUE)
                    .headers(headers)
                    .get();
                Thread.sleep(500);

                final Elements movies = doc.getElementsByClass("product-name");
                final int size = Math.min(movies.size(), moviesCount);
                if (size == 0) {
                    break;
                }
                for (int i = 0; i < size; ++i) {
                    parseReviewsPage(movies
                            .get(i)
                            .attributes()
                            .get("href"),
                        headers,
                        reviewsPerMovie,
                        jsonWriter);
                    /*if ((page * i) % 100 == 0) {
                        logger.debug("Парсер остановился на 30 секунд, чтобы сайт не забанил за большое количество запросов");
                        Thread.sleep(30000);
                        logger.debug("Парсер продолжает работу");
                    }*/
                }
                moviesCount -= size;
            }
        } catch (Exception anyExc) {
            logger.error("При парсинге возникла ошибка!", anyExc);
        } finally {
            if (jsonWriter != null) {
                jsonWriter.endArray();
                jsonWriter.close();
            }
            logger.debug("Парсинг закончен");
        }
    }

    private static void parseReviewsPage(final String url, final Map<String, String> headers, int reviewsPerMovie,
                                         final JsonWriter jsonWriter) throws IOException, InterruptedException {
        String refererBase = "https://otzovik.com" + url;
        logger.debug(String.format("\tПарсинг страницы %s", refererBase));
        headers.put("referer", refererBase + "1/");

        for (int page = 1; reviewsPerMovie > 0; ++page) {
            headers.put("referer", refererBase + page + "/");
            final Document doc = Jsoup.connect(refererBase + page)
                .timeout(5000)
                .userAgent(userAgent)
                .ignoreContentType(true)
                .method(Connection.Method.GET)
                .ignoreHttpErrors(true)
                .maxBodySize(Integer.MAX_VALUE)
                .headers(headers)
                .get();

            final Elements reviews = doc.getElementsByClass("review-btn review-read-link");
            final int size = Math.min(reviews.size(), reviewsPerMovie);
            if (size == 0) {
                break;
            }
            reviewsPerMovie -= size;
            for (int i = 0; i < size; ++i) {
                parseAndSaveReview(reviews
                        .get(i)
                        .attributes()
                        .get("href"),
                    headers,
                    jsonWriter);
            }
        }
    }

    private static void parseAndSaveReview(final String url, final Map<String, String> headers,
                                           final JsonWriter jsonWriter) throws IOException, InterruptedException {
        logger.debug("\t\tПарсинг отзыва https://otzovik.com" + url);
        final Document review = Jsoup.connect("https://otzovik.com" + url)
            .timeout(5000)
            .userAgent(userAgent)
            .ignoreContentType(true)
            .ignoreHttpErrors(true)
            .method(Connection.Method.GET)
            .maxBodySize(Integer.MAX_VALUE)
            .headers(headers)
            .get();
        Thread.sleep(500);

        jsonWriter.beginObject();
        jsonWriter.name("id").value(url.substring(url.indexOf('_') + 1, url.lastIndexOf('.')));
        jsonWriter.name("plus").value(review.getElementsByClass("review-plus")
            .text());
        jsonWriter.name("minus").value(review.getElementsByClass("review-minus")
            .text());
        jsonWriter.name("body").value(review.getElementsByClass("review-body description")
            .text());
        jsonWriter.name("rating").value(Integer.parseInt(
            review.getElementsByClass("rating")
                .get(0)
                .attributes()
                .get("title"))
        );
        jsonWriter.name("recommend").value(review
            .select("td[class~=recommend-ratio]")
            .text()
        );

        final Elements aspects = review.getElementsByClass("rating-item tooltip-top");
        Integer plot = null, spectacularity = null, music = null, actors = null, originality = null;
        int spaceIndex;
        for (int i = 0; i < aspects.size(); ++i) {
            final String aspectText = aspects.get(i)
                .attributes()
                .get("title");
            spaceIndex = aspectText.indexOf(':') + 1;
            int grade = Integer.parseInt(aspectText
                .substring(spaceIndex + 1, spaceIndex + 2));
            if (i == 0) {
                plot = grade;
            } else if (i == 1) {
                spectacularity = grade;
            } else if (i == 2) {
                actors = grade;
            } else if (i == 3) {
                originality = grade;
            } else if (i == 4) {
                music = grade;
            }
        }
        jsonWriter.name("plot").value(plot);
        jsonWriter.name("spectacularity").value(spectacularity);
        jsonWriter.name("music").value(music);
        jsonWriter.name("actors").value(actors);
        jsonWriter.name("originality").value(originality);
        jsonWriter.endObject();
    }
}