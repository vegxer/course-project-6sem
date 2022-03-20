import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.select.Elements;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class OtzovikParser {
    private static final String url = "https://otzovik.com/show_filter.php?cat_id=117&order=date_desc&f[r]=%d_&page=%d";
    private static final String userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36 OPR/83.0.4254.70";

    public static void parse(int moviesCount, final int reviewsPerMovie, final int minimumReviewsPerMovie,
                             final String outputPath) throws IOException {
        final Map<String, String> headers = new HashMap<>(
            Map.of("accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                "accept-encoding", "gzip, deflate, br",
                "accept-language", "en-US,en;q=0.9",
                "cache-control", "max-age=0",
                "cookie", "ssid=978101471; refreg=1647354570~https%3A%2F%2Fyandex.ru%2F; pr_form=advanced; yec=1; ROBINBOBIN=d965c85ed1dbae45523649fec7",
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

        for (int page = 1; moviesCount > 0; ++page) {
            final String referer = headers.get("referer");
            headers.put("referer", referer.substring(referer.lastIndexOf('=') + 1) + page);
            final Document doc = Jsoup.connect(String.format(url, minimumReviewsPerMovie, page))
                .timeout(3000)
                .headers(headers)
                .get();

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
                    outputPath);
            }
            moviesCount -= size;
        }
    }

    private static void parseReviewsPage(final String url, final Map<String, String> headers, int reviewsPerMovie,
                                         final String outputPath) throws IOException {
        String pathBase = url;
        String refererBase = "https://otzovik.com" + url;
        headers.put("referer", refererBase + "1/");

        for (int page = 1; reviewsPerMovie > 0; ++page) {
            headers.put("referer", refererBase + page + "/");
            final Document doc = Jsoup.connect(refererBase + page)
                .timeout(3000)
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
                    outputPath);
            }
        }
    }

    private static void parseAndSaveReview(final String url, final Map<String, String> headers, final String outputPath) throws IOException {
        final Document review = Jsoup.connect("https://otzovik.com" + url)
            .timeout(3000)
            .headers(headers)
            .get();

        final String pros = review.getElementsByClass("review-plus")
            .text();
        final String cons = review.getElementsByClass("review-minus")
            .text();
        final String reviewBody = review.getElementsByClass("review-body description")
            .text();
        final Integer rating = Integer.parseInt(review.getElementsByClass("rating")
            .get(0)
            .attributes()
            .get("title"));
        final String recommendToFriends = review.getElementsByClass("recommend-ratio yes")
            .text();
        Elements aspects = review.getElementsByClass("rating-item tooltip-top");
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
    }
}
