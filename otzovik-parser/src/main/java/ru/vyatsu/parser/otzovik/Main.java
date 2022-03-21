package ru.vyatsu.parser.otzovik;

import java.io.IOException;
import java.util.Scanner;

public class Main {
    public static void main(String[] args) throws IOException {
        final Scanner scanner = new Scanner(System.in);
        System.out.println("Добро пожаловать в программу для сбора отзывов с сайта otzovik.com!\n" +
            "Для начала введите параметры парсинга:");

        System.out.print("Количество фильмов: ");
        final int filmsCount = getNumberFromInput(scanner);
        System.out.print("Количество отзывов за фильм: ");
        final int reviewsPerMovie = getNumberFromInput(scanner);
        System.out.print("При сборе брать фильмы с количеством отзывов от: ");
        final int minimumReviewsPerMovie = getNumberFromInput(scanner);
        System.out.print("Путь для сохранения результатов: ");
        final String path = scanner.nextLine();

        OtzovikParser.parse(filmsCount, reviewsPerMovie, minimumReviewsPerMovie, path);
    }

    public static int getNumberFromInput(final Scanner scanner) {
        int number = 0;
        while (number <= 0) {
            try {
                number = Integer.parseInt(scanner.nextLine());
                if (number <= 0) {
                    System.out.print("Число должно быть больше 0! Попробуйте ещё раз: ");
                }
            } catch (Exception anyExc) {
                System.out.print("Необходимо натуральное число! Попробуйте ещё раз: ");
            }
        }
        return number;
    }
}
