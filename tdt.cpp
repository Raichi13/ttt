#include <string>
#include <vector>
#include <random>
#include <algorithm>
#include <iostream>
#include <map>

class TdT
{
private:
    std::string target_bases;
    int reaction_cycle;
    double miss_extension_probability;
    double deletion_probability;
    double over_extension_probability;
    int miss_extension_count;
    int deletion_count;
    int over_extension_count;
    std::vector<std::string> synthesis_product;

public:
    TdT(std::string target_bases, int reaction_cycle, double miss_extension_probability, double deletion_probability, double over_extension_probability)
    {
        this->target_bases = target_bases;
        this->reaction_cycle = reaction_cycle;
        this->miss_extension_probability = miss_extension_probability;
        this->deletion_probability = deletion_probability;
        this->over_extension_probability = over_extension_probability;
        this->miss_extension_count = 0;
        this->deletion_count = 0;
        this->over_extension_count = 0;
    }

    int weighted_random_exclusive(int probability0, int probability1)
    {
        std::random_device rnd;
        std::mt19937 mt(rnd());
        std::vector<int> v = {0, 1};
        std::shuffle(v.begin(), v.end(), mt);
        if (v[0] < probability0)
        {
            return 0;
        }
        else if (v[0] < probability0 + probability1)
        {
            return 1;
        }
        else
        {
            return -1;
        }
    }

    bool weighted_random(double probability)
    {
        std::random_device rnd;
        std::mt19937 mt(rnd());
        std::uniform_real_distribution<> rand100(0, 1);
        return (rand100(mt) < probability);
    }
    vector<int> extension(string base)
    {
        vector<string> bases_list = {"A", "G", "C", "T"};
        vector<int> r;
        for (int i = 0; i < reaction_cycle; i++)
        {
            string ext_base = base;
            if (weighted_random(miss_extension_probability))
            { // 塩基ミス
                vector<string> other_bases;
                for (auto s : bases_list)
                {
                    if (s != base)
                    {
                        other_bases.push_back(s);
                    }
                }
                ext_base = other_bases[random.randint(0, 2)];
                miss_extension_count += 1;
            }
            // 伸長失敗と過剰に伸長
            int deletion_or_over = weighted_random_exclusive(over_extension_probability, deletion_probability);
            if (deletion_or_over == -1)
            { // 正常に伸長
                r.push_back(ext_base);
                continue;
            }
            if (deletion_or_over == 0)
            { // 過剰に伸長
                r.push_back(ext_base);
                r.push_back(ext_base);
                over_extension_count += 1;
                continue;
            }
            if (deletion_or_over == 1)
            { // 欠損
                deletion_count += 1;
                continue;
            }
        }
        return r;
    }
}