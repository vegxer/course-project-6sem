package ru.vyatsu.parser.otzovik.statistics;

import com.google.gson.stream.JsonWriter;
import org.apache.commons.lang3.math.NumberUtils;

import java.io.IOException;

public class Evaluated {
    public Integer oneStarsCount = 0;
    public Integer twoStarsCount = 0;
    public Integer threeStarsCount = 0;
    public Integer fourStarsCount = 0;
    public Integer fiveStarsCount = 0;

    public void incRating(final Integer rating) {
        if (rating == 1) {
            ++oneStarsCount;
        } else if (rating == 2) {
            ++twoStarsCount;
        } else if (rating == 3) {
            ++threeStarsCount;
        } else if (rating == 4) {
            ++fourStarsCount;
        } else if (rating == 5) {
            ++fiveStarsCount;
        }
    }

    public Integer getModa() {
        int max = NumberUtils.max(
            oneStarsCount,
            twoStarsCount,
            threeStarsCount,
            fourStarsCount,
            fiveStarsCount
        );
        if (max == oneStarsCount) {
            return 1;
        }
        if (max == twoStarsCount) {
            return 2;
        }
        if (max == threeStarsCount) {
            return 3;
        }
        if (max == fourStarsCount) {
            return 4;
        }
        return 5;
    }

    public Double getAverage() {
        double sum = oneStarsCount + twoStarsCount + threeStarsCount + fourStarsCount + fiveStarsCount;
        if (sum == 0) {
            return null;
        }
        return (oneStarsCount + 2 * threeStarsCount + 3 * threeStarsCount + 4 * fourStarsCount + 5 * fiveStarsCount) / sum;
    }

    public Integer getMedian() {
        double sum = oneStarsCount + twoStarsCount + threeStarsCount + fourStarsCount + fiveStarsCount;
        int currSum = oneStarsCount;
        if (currSum >= sum / 2) {
            return 1;
        }
        currSum += twoStarsCount;
        if (currSum >= sum / 2) {
            return 2;
        }
        currSum += threeStarsCount;
        if (currSum >= sum / 2) {
            return 3;
        }
        currSum += fourStarsCount;
        if (currSum >= sum / 2) {
            return 4;
        }
        return 5;
    }

    public void writeToJson(final JsonWriter writer) throws IOException {
        writer.beginObject();
        writer.name("oneStarCount").value(oneStarsCount);
        writer.name("twoStarCount").value(twoStarsCount);
        writer.name("threeStarCount").value(threeStarsCount);
        writer.name("fourStarCount").value(fourStarsCount);
        writer.name("fiveStarCount").value(fiveStarsCount);
        writer.name("moda").value(getModa());
        writer.name("median").value(getMedian());
        writer.name("average").value(getAverage());
        writer.endObject();
    }
}
