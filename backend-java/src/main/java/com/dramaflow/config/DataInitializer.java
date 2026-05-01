package com.dramaflow.config;

import com.dramaflow.model.Category;
import com.dramaflow.model.Drama;
import com.dramaflow.model.Episode;
import com.dramaflow.repository.CategoryRepository;
import com.dramaflow.repository.DramaRepository;
import com.dramaflow.repository.EpisodeRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class DataInitializer implements CommandLineRunner {

    private final CategoryRepository categoryRepository;
    private final DramaRepository dramaRepository;
    private final EpisodeRepository episodeRepository;

    public DataInitializer(CategoryRepository categoryRepository,
                           DramaRepository dramaRepository,
                           EpisodeRepository episodeRepository) {
        this.categoryRepository = categoryRepository;
        this.dramaRepository = dramaRepository;
        this.episodeRepository = episodeRepository;
    }

    @Override
    public void run(String... args) {
        if (categoryRepository.count() > 0) {
            return; // 数据已存在，跳过
        }

        Category c1 = categoryRepository.save(new Category("甜宠", "romance", 1));
        Category c2 = categoryRepository.save(new Category("悬疑", "suspense", 2));
        Category c3 = categoryRepository.save(new Category("搞笑", "comedy", 3));
        Category c4 = categoryRepository.save(new Category("奇幻", "fantasy", 4));
        Category c5 = categoryRepository.save(new Category("霸总", "president", 5));

        Drama d1 = createDrama("重生之女王归来", "她是商界女王，却遭人暗算重生回到十年前...", c4, 4.8, 2025, "ongoing");
        Drama d2 = createDrama("霸道总裁爱上我", "平凡女孩意外闯入总裁的世界...", c5, 4.9, 2025, "ongoing");
        Drama d3 = createDrama("我的房东是财阀", "为了省钱租了个地下室，没想到房东竟是...", c3, 4.6, 2025, "completed");
        Drama d4 = createDrama("深渊回响", "每个谎言都有回响，每个真相都有代价...", c2, 4.7, 2024, "completed");
        Drama d5 = createDrama("契约婚姻", "一场契约开始的婚姻，却在不经意间动了真心...", c1, 4.5, 2025, "ongoing");

        for (Drama d : new Drama[]{d1, d2, d3, d4, d5}) {
            for (int i = 1; i <= 10; i++) {
                Episode ep = new Episode();
                ep.setDrama(d);
                ep.setEpisodeNumber(i);
                ep.setTitle("第" + i + "集");
                ep.setDuration(String.format("%d:%02d", 18 + i % 5, i * 4));
                ep.setVideoUrl(String.format("/videos/drama%02d_ep%02d.mp4", d.getId(), i));
                episodeRepository.save(ep);
            }
        }
    }

    private Drama createDrama(String title, String description, Category category,
                              double rating, int year, String status) {
        Drama d = new Drama();
        d.setTitle(title);
        d.setDescription(description);
        d.setCategory(category);
        d.setRating(rating);
        d.setCoverUrl("/covers/drama" + (dramaRepository.count() + 1) + ".jpg");
        d.setYear(year);
        d.setStatus(status);
        return dramaRepository.save(d);
    }
}
