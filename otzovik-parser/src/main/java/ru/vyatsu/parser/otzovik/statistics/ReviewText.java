package ru.vyatsu.parser.otzovik.statistics;

import com.google.gson.stream.JsonWriter;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class ReviewText {
    public List<Integer> lengths = new ArrayList<>();

    public Double getAverage() {
        if (lengths.size() == 0) {
            return null;
        }
        return getSum() / lengths.size();
    }

    public Integer getMedian() {
        if (lengths.size() == 0) {
            return null;
        }
        lengths.sort(Comparator.naturalOrder());

        final double subSum = getSum() / 2;
        int i = 0;
        for (double currSum = 0; currSum < subSum; currSum += lengths.get(i++));
        return lengths.get(i - 1);
    }

    public Integer getMin() {
        if (lengths.size() == 0) {
            return null;
        }
        int min = lengths.get(0);
        for (int i = 1; i < lengths.size(); ++i) {
            if (lengths.get(i) < min) {
                min = lengths.get(i);
            }
        }
        return min;
    }

    public Integer getMax() {
        if (lengths.size() == 0) {
            return null;
        }
        int max = lengths.get(0);
        for (int i = 1; i < lengths.size(); ++i) {
            if (lengths.get(i) > max) {
                max = lengths.get(i);
            }
        }
        return max;
    }

    public void writeToJson(final JsonWriter writer) throws IOException {
        writer.beginObject();
        writer.name("average").value(getAverage());
        writer.name("min").value(getMin());
        writer.name("max").value(getMax());
        writer.name("median").value(getMedian());
        writer.endObject();
    }

    private double getSum() {
        double sum = 0;
        for (int length: lengths) {
            sum += length;
        }
        return sum;
    }
}
