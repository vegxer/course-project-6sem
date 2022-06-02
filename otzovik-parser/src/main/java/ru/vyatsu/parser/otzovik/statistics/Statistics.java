package ru.vyatsu.parser.otzovik.statistics;

public class Statistics {
    public Integer moviesCount = 0;
    public ReviewText pluses = new ReviewText();
    public ReviewText minuses = new ReviewText();
    public ReviewText body = new ReviewText();
    public Evaluated rating = new Evaluated();
    public Evaluated actors = new Evaluated();
    public Evaluated music = new Evaluated();
    public Evaluated spectacularity = new Evaluated();
    public Evaluated plot = new Evaluated();
    public Evaluated originality = new Evaluated();
}
