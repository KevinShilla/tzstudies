import java.io.File;
import java.util.*;
import java.util.regex.Pattern;

public class FileReport {
    // Matches: Subject-F2-2021.pdf OR Subject - S7 - 2016.pdf
    private static final Pattern DASHES = Pattern.compile("\\s*-\\s*");

    private static String[] parse(String filename) {
        String name = filename.replace(".pdf", "");
        // normalize separators to "-"
        String cleaned = DASHES.matcher(name.trim()).replaceAll("-");
        cleaned = cleaned.replace(" - ", "-");
        String[] parts = cleaned.split("-");
        List<String> p = new ArrayList<>();
        for (String part : parts) {
            String s = part.trim();
            if (!s.isEmpty()) p.add(s);
        }
        String subject = p.size() >= 1 ? p.get(0) : name;
        String level   = p.size() >= 2 ? p.get(1) : "";
        String year    = p.size() >= 3 ? p.get(2) : "";
        return new String[]{subject, level, year};
    }

    public static void main(String[] args) {
        File examsDir = new File("exams");
        if (!examsDir.exists() || !examsDir.isDirectory()) {
            System.out.println("Could not find exams/ folder. Run this from the project root.");
            return;
        }

        Set<String> subjects = new TreeSet<>();
        Set<String> levels   = new TreeSet<>();
        Set<String> years    = new TreeSet<>();
        List<String> weird   = new ArrayList<>();

        File[] files = examsDir.listFiles();
        if (files == null) files = new File[0];

        for (File f : files) {
            String name = f.getName();
            if (!name.toLowerCase().endsWith(".pdf")) continue;

            String[] parsed = parse(name);
            String subject = parsed[0];
            String level   = parsed[1];
            String year    = parsed[2];

            subjects.add(subject);
            if (!level.isEmpty()) levels.add(level);
            if (!year.isEmpty()) years.add(year);

            if (level.isEmpty() || year.isEmpty()) {
                weird.add(name);
            }
        }

        System.out.println("=== TZStudies Exams Report (Java) ===");
        System.out.println("Total PDFs: " + (subjects.size() > 0 ? "" : "0"));
        System.out.println();

        System.out.println("Subjects (" + subjects.size() + "): " + subjects);
        System.out.println("Levels   (" + levels.size() + "): " + levels);
        System.out.println("Years    (" + years.size() + "): " + years);

        if (!weird.isEmpty()) {
            System.out.println();
            System.out.println("Unusual filenames (missing level/year):");
            for (String w : weird) System.out.println(" - " + w);
        }

        System.out.println();
        System.out.println("Done.");
    }
}
