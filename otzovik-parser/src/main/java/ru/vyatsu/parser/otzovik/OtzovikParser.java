package ru.vyatsu.parser.otzovik;

import com.google.gson.stream.JsonWriter;
import org.jsoup.Connection;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.select.Elements;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import ru.vyatsu.parser.otzovik.statistics.Statistics;

import java.awt.*;
import java.io.*;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public class OtzovikParser {
    private static boolean endedTrain = true;
    private static boolean endedTest = true;
    private static final Logger logger = LoggerFactory.getLogger(OtzovikParser.class);
    private static final String url = "https://otzovik.com/show_filter.php?cat_id=117&order=rate&f[r]=%d_&page=%d";
    private static Map<String,String> additionalEntries;

    public static void parse(int moviesCount, final int reviewsPerMovie, final int minimumReviewsPerMovie,
                             final String trainOutputPath, final String trainDatasetStatisticsPath,
                             final String testOutputPath, final String testDatasetStatisticsPath) throws IOException {
        additionalEntries = Map.of("referer", String.format("https://otzovik.com/show_filter.php?cat_id=117&order=date_desc&f[r]=%d_&page=", minimumReviewsPerMovie));
        final Statistics trainStatistics = new Statistics();
        trainStatistics.type = "train";
        final Statistics testStatistics = new Statistics();
        testStatistics.type = "test";
        Map<String, String> headers = readHeaders();

        JsonWriter trainWriter = null;
        JsonWriter testWriter = null;
        try {
            trainWriter = new JsonWriter(new FileWriter(trainOutputPath));
            trainWriter.beginArray();
            testWriter = new JsonWriter(new FileWriter(testOutputPath));
            testWriter.beginArray();
            logger.debug(String.format("Парсинг стартовал. Примерное время ожидания %.2f - %.2f мин.",
                0.75 * moviesCount * reviewsPerMovie / 60,
                0.85 * moviesCount * reviewsPerMovie / 60)
            );
            for (int page = 1; moviesCount > 0; ++page) {
                final String referer = headers.get("referer");
                headers.put("referer", referer.substring(referer.lastIndexOf('=') + 1) + page);
                Document doc;
                try {
                    doc = Jsoup.connect(String.format(url, minimumReviewsPerMovie, page))
                        .timeout(5000)
                        .ignoreContentType(true)
                        .method(Connection.Method.GET)
                        .maxBodySize(Integer.MAX_VALUE)
                        .headers(headers)
                        .get();
                } catch (Exception e) {
                    ((Runnable) Toolkit.getDefaultToolkit().getDesktopProperty("win.sound.exclamation")).run();
                    logger.error("Ошибка при парсинге отзыва. Парсер уснул на 60 секунд. Смените прокси!");
                    if (!endedTrain) {
                        trainWriter.endObject();
                        endedTrain = true;
                    }
                    if (!endedTest) {
                        testWriter.endObject();
                        endedTest = true;
                    }
                    ((Runnable) Toolkit.getDefaultToolkit().getDesktopProperty("win.sound.exclamation")).run();
                    Thread.sleep(60000);
                    headers = readHeaders();
                    continue;
                }
                Thread.sleep(600);

                final Elements movies = doc.getElementsByClass("product-name");
                final int size = Math.min(movies.size(), moviesCount);
                if (size == 0) {
                    break;
                }
                for (int i = 0; i < size; ++i) {
                    try {
                        parseReviewsPage(movies
                                .get(i)
                                .attributes()
                                .get("href"),
                            headers,
                            reviewsPerMovie,
                            trainWriter,
                            testWriter,
                            trainStatistics,
                            testStatistics);
                    } catch (Exception exc) {
                        ((Runnable) Toolkit.getDefaultToolkit().getDesktopProperty("win.sound.exclamation")).run();
                        logger.error("Ошибка при парсинге отзыва. Парсер уснул на 60 секунд. Смените прокси!");
                        if (!endedTrain) {
                            trainWriter.endObject();
                            endedTrain = true;
                        }
                        if (!endedTest) {
                            testWriter.endObject();
                            endedTest = true;
                        }
                        ((Runnable) Toolkit.getDefaultToolkit().getDesktopProperty("win.sound.exclamation")).run();
                        Thread.sleep(60000);
                        headers = readHeaders();
                    }
                }
                moviesCount -= size;
            }
        } catch (Exception anyExc) {
            logger.error("При парсинге возникла ошибка!", anyExc);
        } finally {
            closeWriter(trainWriter);
            closeWriter(testWriter);

            writeStatistics(trainStatistics, trainDatasetStatisticsPath);
            writeStatistics(testStatistics, testDatasetStatisticsPath);

            logger.debug("Парсинг закончен");
        }
    }

    private static void parseReviewsPage(final String url, Map<String, String> headers, int reviewsPerMovie,
                                         final JsonWriter trainWriter, final JsonWriter testWriter,
                                         final Statistics trainStatistics, final Statistics testStatistics) throws IOException, InterruptedException {
        final String refererBase = "https://otzovik.com" + url;
        logger.debug(String.format("\tПарсинг страницы %s", refererBase));
        headers.put("referer", refererBase + "1/");

        for (int page = 2; reviewsPerMovie > 0; ++page) {
            headers.put("referer", refererBase + page + "/");
            final Document doc = Jsoup.connect(refererBase + page)
                .timeout(5000)
                .ignoreContentType(true)
                .method(Connection.Method.GET)
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
                if (i % 2 == 0) {
                    ++trainStatistics.moviesCount;
                } else {
                    ++testStatistics.moviesCount;
                }

                logger.debug(String.format("\t\tПарсинг отзыва https://otzovik.com%s (%d)",
                    url, trainStatistics.moviesCount + testStatistics.moviesCount));
                try {
                    parseAndSaveReview(reviews
                            .get(i)
                            .attributes()
                            .get("href"),
                        headers,
                        i % 2 == 0 ? trainWriter : testWriter,
                        i % 2 == 0 ? trainStatistics : testStatistics);
                } catch (Exception exc) {
                    if (i % 2 == 0) {
                        --trainStatistics.moviesCount;
                    } else {
                        --testStatistics.moviesCount;
                    }
                    ((Runnable) Toolkit.getDefaultToolkit().getDesktopProperty("win.sound.exclamation")).run();
                    logger.error("Ошибка при парсинге отзыва. Парсер уснул на 60 секунд. Смените прокси!");
                    if (!endedTrain) {
                        trainWriter.endObject();
                        endedTrain = true;
                    }
                    if (!endedTest) {
                        testWriter.endObject();
                        endedTest = true;
                    }
                    ((Runnable) Toolkit.getDefaultToolkit().getDesktopProperty("win.sound.exclamation")).run();
                    Thread.sleep(60000);
                    headers = readHeaders();
                }
            }
        }
    }

    private static void parseAndSaveReview(final String url, final Map<String, String> headers,
                                           final JsonWriter jsonWriter, final Statistics statistics) throws IOException, InterruptedException {
        final Document review = Jsoup.connect("https://otzovik.com" + url)
            .timeout(5000)
            .ignoreContentType(true)
            .method(Connection.Method.GET)
            .maxBodySize(Integer.MAX_VALUE)
            .headers(headers)
            .get();
        Thread.sleep(600);

        jsonWriter.beginObject();
        if ("train".equals(statistics.type)) {
            endedTrain = false;
        } else {
            endedTest = false;
        }
        jsonWriter.name("id").value(url.substring(url.indexOf('_') + 1, url.lastIndexOf('.')));

        final String reviewPlus = review.getElementsByClass("review-plus").text();
        jsonWriter.name("plus").value(reviewPlus);
        statistics.pluses.lengths.add(reviewPlus.length());

        final String reviewMinus = review.getElementsByClass("review-minus").text();
        jsonWriter.name("minus").value(reviewMinus);
        statistics.minuses.lengths.add(reviewMinus.length());

        final String reviewBody = review.getElementsByClass("review-body description").text();
        jsonWriter.name("body").value(reviewBody);
        statistics.body.lengths.add(reviewBody.length());

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
        statistics.plot.incRating(plot);
        jsonWriter.name("spectacularity").value(spectacularity);
        statistics.spectacularity.incRating(spectacularity);
        jsonWriter.name("music").value(music);
        statistics.music.incRating(music);
        jsonWriter.name("actors").value(actors);
        statistics.actors.incRating(actors);
        jsonWriter.name("originality").value(originality);
        statistics.originality.incRating(originality);

        final Integer rating = Integer.parseInt(
            review.getElementsByClass("rating")
                .get(0)
                .attributes()
                .get("title"));
        jsonWriter.name("rating").value(rating);
        statistics.rating.incRating(rating);

        jsonWriter.endObject();
        if ("train".equals(statistics.type)) {
            endedTrain = true;
        } else {
            endedTest = true;
        }
    }

    private static void writeStatistics(final Statistics statistics, final String path) throws IOException {
        try (JsonWriter statisticsWriter = new JsonWriter(new FileWriter(path))) {
            statisticsWriter.beginObject();
            statisticsWriter.name("moviesProcessed").value(statistics.moviesCount);
            statisticsWriter.name("minuses");
            statistics.minuses.writeToJson(statisticsWriter);
            statisticsWriter.name("pluses");
            statistics.pluses.writeToJson(statisticsWriter);
            statisticsWriter.name("body");
            statistics.body.writeToJson(statisticsWriter);
            statisticsWriter.name("rating");
            statistics.rating.writeToJson(statisticsWriter);
            statisticsWriter.name("actors");
            statistics.actors.writeToJson(statisticsWriter);
            statisticsWriter.name("music");
            statistics.music.writeToJson(statisticsWriter);
            statisticsWriter.name("originality");
            statistics.originality.writeToJson(statisticsWriter);
            statisticsWriter.name("spectacularity");
            statistics.spectacularity.writeToJson(statisticsWriter);
            statisticsWriter.name("plot");
            statistics.plot.writeToJson(statisticsWriter);
            statisticsWriter.endObject();
        }
    }

    private static void closeWriter(JsonWriter writer) {
        if (writer != null) {
            try {
                writer.endArray();
                writer.close();
            } catch (Exception writerExc) {
                logger.error("Не удалось корректно закончить файл", writerExc);
            }
        }
    }

    private static Map<String, String> readHeaders() throws IOException {
        List<String> fileLines;
        try (final BufferedReader reader = new BufferedReader(new FileReader("headers.txt"))) {
            fileLines = reader.lines().collect(Collectors.toList());
        }
        HashMap<String, String> headers = new HashMap<>();
        for (final String line : fileLines) {
            if ("throwException".equals(line)) {
                throw new IllegalArgumentException();
            }
            final String[] split = line.split("\\|");
            headers.put(split[0], split[1]);
        }
        headers.putAll(additionalEntries);
        return headers;
    }
}
