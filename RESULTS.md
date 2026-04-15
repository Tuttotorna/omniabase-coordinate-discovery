# Results

This file records the first experimental results for **Omniabase Coordinate Discovery**.

The purpose of this repository is not to use Omniabase as a truth gate, but as a multi-representation engine for discovering latent coordinates, regime signatures, and early transition markers in dynamical systems.

The first testbed is the logistic map.

---

## Experiment 1 - Logistic map multibase signatures v0

### System

Logistic map:

`x_(n+1) = r * x_n * (1 - x_n)`

### Initial settings

- system: logistic map
- initial state: `x0 = 0.123456`
- total iterations: `300`
- burn-in: `100`
- bases: `2` to `16`
- decimal precision per state: `12` digits

### Tested r values

- `3.50`
- `3.55`
- `3.60`
- `3.70`
- `3.80`
- `3.90`
- `4.00`

### Extracted minimal signatures

For each state after burn-in, the prototype extracted:

- `avg_digit_sum`
- `digit_sum_span`
- `avg_repetition`
- `repetition_span`

These were computed across the same scalar state represented simultaneously in bases 2 through 16.

### Run command

```bash
python experiments/logistic_map_multibase_v0.py

Observed output

Done. Wrote outputs/logistic_map_multibase_v0.csv

Sample rows from outputs/logistic_map_multibase_v0.csv

r	step	x	avg_digit_sum	digit_sum_span	avg_repetition	repetition_span

3.5	0	0.826940706691121516	45.53333333333333	42.0	0.048484848484848485	0.18181818181818182
3.5	1	0.500884210333256151	46.46666666666667	45.0	0.04848484848484848	0.18181818181818182
3.5	2	0.874997223405763071	47.733333333333334	43.0	0.06060606060606061	0.18181818181818182
3.5	3	0.382819842525150937	47.733333333333334	46.0	0.04242424242424243	0.18181818181818182


Immediate observation

At r = 3.5, the logistic map falls into a clear period-4 cycle.

The extracted Omniabase signatures repeat with the same cycle, showing that the method is not producing arbitrary noise. It is tracking regime structure in a representation-sensitive way.


---

Experiment 2 - Regime summary across coarse r values

Purpose

The second step summarized each regime rather than inspecting only raw rows.

This was done to test whether Omniabase signatures separate dynamical regimes at the level of regime-wide statistics.

Run command

python experiments/analyze_logistic_map_multibase_v0.py

Observed console output

------------------------------------------------------------
r = 3.50
 n_steps: 200
 unique_states_rounded_12: 4
 x_std: 0.207851609139
 x_mean_abs_step_diff: 0.320490074258
 avg_digit_sum_std: 0.982061324177
 avg_digit_sum_mean_abs_step_diff: 1.516666666667
 digit_sum_span_std: 1.639359631075
 avg_repetition_std: 0.006659775084
 repetition_span_std: 0.000000000000
------------------------------------------------------------
r = 3.55
 n_steps: 200
 unique_states_rounded_12: 8
 x_std: 0.210459521360
 x_mean_abs_step_diff: 0.268735503061
 avg_digit_sum_std: 1.071649170425
 avg_digit_sum_mean_abs_step_diff: 1.488442211055
 digit_sum_span_std: 2.149273132945
 avg_repetition_std: 0.005574542618
 repetition_span_std: 0.040600109033
------------------------------------------------------------
r = 3.60
 n_steps: 200
 unique_states_rounded_12: 200
 x_std: 0.212003732688
 x_mean_abs_step_diff: 0.213969512392
 avg_digit_sum_std: 1.206263884323
 avg_digit_sum_mean_abs_step_diff: 1.341172529313
 digit_sum_span_std: 3.166348448924
 avg_repetition_std: 0.007629551468
 repetition_span_std: 0.051910609322
------------------------------------------------------------
r = 3.70
 n_steps: 200
 unique_states_rounded_12: 200
 x_std: 0.224647953255
 x_mean_abs_step_diff: 0.245803926038
 avg_digit_sum_std: 1.107063462499
 avg_digit_sum_mean_abs_step_diff: 1.258266331658
 digit_sum_span_std: 3.522641054663
 avg_repetition_std: 0.008453472093
 repetition_span_std: 0.063231454558
------------------------------------------------------------
r = 3.80
 n_steps: 200
 unique_states_rounded_12: 200
 x_std: 0.246440265780
 x_mean_abs_step_diff: 0.281898517228
 avg_digit_sum_std: 1.238426037355
 avg_digit_sum_mean_abs_step_diff: 1.402445561139
 digit_sum_span_std: 3.744111376548
 avg_repetition_std: 0.008594248464
 repetition_span_std: 0.060144574932
------------------------------------------------------------
r = 3.90
 n_steps: 200
 unique_states_rounded_12: 200
 x_std: 0.269476902677
 x_mean_abs_step_diff: 0.315144170792
 avg_digit_sum_std: 1.264213854117
 avg_digit_sum_mean_abs_step_diff: 1.455611390285
 digit_sum_span_std: 3.504812405821
 avg_repetition_std: 0.008298758838
 repetition_span_std: 0.065842183350
------------------------------------------------------------
r = 4.00
 n_steps: 200
 unique_states_rounded_12: 200
 x_std: 0.291776964893
 x_mean_abs_step_diff: 0.342921949514
 avg_digit_sum_std: 1.159385552351
 avg_digit_sum_mean_abs_step_diff: 1.353366834171
 digit_sum_span_std: 3.516086318622
 avg_repetition_std: 0.009497486801
 repetition_span_std: 0.066465369614
------------------------------------------------------------
Done. Wrote outputs/logistic_map_multibase_v0_summary.csv

Condensed regime summary

r	unique_states	x_std	avg_digit_sum_std	digit_sum_span_std	repetition_span_std

3.5	4	0.2078516	0.9820613	1.6393596	0.0000000
3.55	8	0.2104595	1.0716491	2.1492731	0.0406001
3.6	200	0.2120037	1.2062638	3.1663484	0.0519106
3.7	200	0.2246479	1.1070634	3.5226410	0.0632314
3.8	200	0.2464402	1.2384260	3.7441113	0.0601445
3.9	200	0.2694769	1.2642138	3.5048124	0.0658421
4.0	200	0.2917769	1.1593855	3.5160863	0.0664653


Main result

The Omniabase signatures do not saturate when the simple unique_states count saturates.

From r = 3.6 onward, unique_states_rounded_12 stays at 200, but the multi-base signatures continue to move.

This suggests that Omniabase is not merely tracking obvious periodicity. It is still extracting differentiating structure inside already-chaotic regimes.


---

Experiment 3 - Fine-grained transition scan around the bifurcation region

Purpose

The third step densified r around the critical transition region:

from 3.540 to 3.610

step size: 0.002


This was designed to test the key question:

Does Omniabase amplify transition boundaries more clearly than standard simple statistics such as x_std?

Run command

python experiments/logistic_map_regime_scan_v1.py

Observed output

Done. Wrote outputs/logistic_map_regime_scan_v1.csv

Full transition scan summary

r	unique_states	x_std	avg_digit_sum_std	digit_sum_span_std	avg_repetition_std	repetition_span_std

3.540	4	0.20914972	0.99343399	1.81231895	0.00755358	0.00000000
3.542	4	0.20930776	1.00697567	1.83425734	0.00760451	0.00000000
3.544	8	0.20963384	1.03756857	1.95400230	0.00657929	0.02682977
3.546	8	0.20980481	1.04944122	2.01633950	0.00612185	0.03531086
3.548	8	0.20997787	1.05943615	2.07228738	0.00586937	0.04060010
3.550	8	0.21015307	1.07164917	2.14927313	0.00557454	0.04060010
3.552	8	0.21033045	1.08272547	2.19730030	0.00529528	0.04060010
3.554	8	0.21051004	1.09650000	2.27211355	0.00511528	0.04060010
3.556	8	0.21069189	1.10777555	2.33304522	0.00515152	0.04060010
3.558	8	0.21087602	1.12196024	2.40870814	0.00550428	0.04060010
3.560	8	0.21106250	1.13783457	2.47853283	0.00595300	0.04060010
3.562	8	0.21125134	1.15560942	2.58069757	0.00654131	0.04060010
3.564	8	0.21144259	1.17195705	2.65922333	0.00713781	0.04060010
3.566	16	0.21153139	1.19256910	2.84650630	0.00762145	0.04944882
3.568	243	0.21155990	1.19934251	2.92055620	0.00762181	0.05284358
3.570	250	0.21160416	1.19665798	2.95155107	0.00771809	0.05293208
3.572	250	0.21163155	1.20573733	3.01691285	0.00770542	0.05364175
3.574	250	0.21165431	1.18957448	2.93297598	0.00752763	0.05193635
3.576	250	0.21168170	1.18880622	2.97305942	0.00769351	0.05187424
3.578	250	0.21172159	1.18247012	2.94635156	0.00768291	0.05139884
3.580	250	0.21176161	1.19830848	3.03157204	0.00774635	0.05141011
3.582	250	0.21180295	1.18131377	3.01168340	0.00759908	0.04996256
3.584	250	0.21184699	1.19532464	3.06421584	0.00742183	0.04961726
3.586	250	0.21189396	1.20817340	3.12579133	0.00746654	0.04892404
3.588	250	0.21194285	1.19946821	3.13632946	0.00757279	0.04899385
3.590	250	0.21199342	1.19958744	3.15523910	0.00761265	0.04953935
3.592	250	0.21204689	1.20015501	3.16104764	0.00741270	0.05141206
3.594	250	0.21210166	1.19163618	3.12071833	0.00735870	0.05151515
3.596	250	0.21216010	1.18780287	3.14652433	0.00739818	0.05151515
3.598	250	0.21221976	1.19472659	3.17646698	0.00753696	0.05151515
3.600	250	0.21228227	1.20626388	3.16634845	0.00762955	0.05191061
3.602	250	0.21234720	1.19448375	3.14923145	0.00763863	0.05193420
3.604	250	0.21241470	1.19069150	3.15838081	0.00751998	0.05193420
3.606	250	0.21248464	1.20455015	3.20815454	0.00754876	0.05191061
3.608	250	0.21255755	1.18378524	3.13627581	0.00742512	0.05202450
3.610	250	0.21263155	1.19828552	3.19794033	0.00738670	0.05215007


Main result

Transition 1: period-4 to period-8

At:

r = 3.542 -> unique_states = 4

r = 3.544 -> unique_states = 8


The standard scalar statistic x_std changes only weakly:

0.20930776 -> 0.20963384


But repetition_span_std jumps from:

0.00000000

to 0.02682977


This means Omniabase detects a clean structural break where the visible scalar variance changes only minimally.

Transition 2: pre-chaotic to chaotic regime

Around:

r = 3.564 -> unique_states = 8

r = 3.566 -> unique_states = 16

r = 3.568 -> unique_states = 243


Again, x_std remains almost flat:

0.21144259

0.21153139

0.21155990


But digit_sum_span_std rises much more clearly:

2.65922333

2.84650630

2.92055620


This suggests that Omniabase signatures may act as regime-transition amplifiers even when simple scalar statistics barely move.


---

Experiment 4 - Delta sensitivity across the transition scan

Purpose

The fourth step tested the harder question:

Does Omniabase detect transitions earlier, or merely more noisily?

To answer this, the scan around the bifurcation region was converted into step-to-step deltas.

The following were compared:

delta_x_std

delta_digit_sum_span_std

delta_repetition_span_std


Run command

python experiments/analyze_regime_scan_deltas_v1.py

Observed console output

------------------------------------------------------------------------
3.540 -> 3.542 | states 4 -> 4 | d_x_std=0.00015804 | d_digit_span=0.02193839 | d_rep_span=0.00000000
3.542 -> 3.544 | states 4 -> 8 | d_x_std=0.00032608 | d_digit_span=0.11974496 | d_rep_span=0.02682977
3.544 -> 3.546 | states 8 -> 8 | d_x_std=0.00017097 | d_digit_span=0.06233720 | d_rep_span=0.00848109
3.546 -> 3.548 | states 8 -> 8 | d_x_std=0.00017306 | d_digit_span=0.05594788 | d_rep_span=0.00528924
3.548 -> 3.550 | states 8 -> 8 | d_x_std=0.00017520 | d_digit_span=0.07698575 | d_rep_span=0.00000000
3.550 -> 3.552 | states 8 -> 8 | d_x_std=0.00017738 | d_digit_span=0.04802717 | d_rep_span=0.00000000
3.552 -> 3.554 | states 8 -> 8 | d_x_std=0.00017959 | d_digit_span=0.07481325 | d_rep_span=0.00000000
3.554 -> 3.556 | states 8 -> 8 | d_x_std=0.00018185 | d_digit_span=0.06093167 | d_rep_span=0.00000000
3.556 -> 3.558 | states 8 -> 8 | d_x_std=0.00018413 | d_digit_span=0.07566292 | d_rep_span=0.00000000
3.558 -> 3.560 | states 8 -> 8 | d_x_std=0.00018648 | d_digit_span=0.06982469 | d_rep_span=0.00000000
3.560 -> 3.562 | states 8 -> 8 | d_x_std=0.00018884 | d_digit_span=0.10216474 | d_rep_span=0.00000000
3.562 -> 3.564 | states 8 -> 8 | d_x_std=0.00019125 | d_digit_span=0.07852576 | d_rep_span=0.00000000
3.564 -> 3.566 | states 8 -> 16 | d_x_std=0.00008880 | d_digit_span=0.18728297 | d_rep_span=0.00884872
3.566 -> 3.568 | states 16 -> 243 | d_x_std=0.00002851 | d_digit_span=0.07404990 | d_rep_span=0.00339476
3.568 -> 3.570 | states 243 -> 250 | d_x_std=0.00004426 | d_digit_span=0.03099487 | d_rep_span=0.00008850
3.570 -> 3.572 | states 250 -> 250 | d_x_std=0.00002739 | d_digit_span=0.06536178 | d_rep_span=0.00070967
3.572 -> 3.574 | states 250 -> 250 | d_x_std=0.00002276 | d_digit_span=-0.08393687 | d_rep_span=-0.00170540
3.574 -> 3.576 | states 250 -> 250 | d_x_std=0.00002739 | d_digit_span=0.04008344 | d_rep_span=-0.00006211
3.576 -> 3.578 | states 250 -> 250 | d_x_std=0.00003989 | d_digit_span=-0.02670786 | d_rep_span=-0.00047540
3.578 -> 3.580 | states 250 -> 250 | d_x_std=0.00004002 | d_digit_span=0.08522048 | d_rep_span=0.00001127
3.580 -> 3.582 | states 250 -> 250 | d_x_std=0.00004134 | d_digit_span=-0.01988864 | d_rep_span=-0.00144755
3.582 -> 3.584 | states 250 -> 250 | d_x_std=0.00004404 | d_digit_span=0.05253244 | d_rep_span=-0.00034530
3.584 -> 3.586 | states 250 -> 250 | d_x_std=0.00004697 | d_digit_span=0.06157549 | d_rep_span=-0.00069322
3.586 -> 3.588 | states 250 -> 250 | d_x_std=0.00004889 | d_digit_span=0.01053813 | d_rep_span=0.00006981
3.588 -> 3.590 | states 250 -> 250 | d_x_std=0.00005057 | d_digit_span=0.01890964 | d_rep_span=0.00054550
3.590 -> 3.592 | states 250 -> 250 | d_x_std=0.00005347 | d_digit_span=0.00580854 | d_rep_span=0.00187271
3.592 -> 3.594 | states 250 -> 250 | d_x_std=0.00005477 | d_digit_span=-0.04032931 | d_rep_span=0.00010309
3.594 -> 3.596 | states 250 -> 250 | d_x_std=0.00005844 | d_digit_span=0.02580600 | d_rep_span=0.00000000
3.596 -> 3.598 | states 250 -> 250 | d_x_std=0.00005966 | d_digit_span=0.02994265 | d_rep_span=0.00000000
3.598 -> 3.600 | states 250 -> 250 | d_x_std=0.00006251 | d_digit_span=-0.01011853 | d_rep_span=0.00039546
3.600 -> 3.602 | states 250 -> 250 | d_x_std=0.00006493 | d_digit_span=-0.01711700 | d_rep_span=0.00002359
3.602 -> 3.604 | states 250 -> 250 | d_x_std=0.00006750 | d_digit_span=0.00914936 | d_rep_span=0.00000000
3.604 -> 3.606 | states 250 -> 250 | d_x_std=0.00006994 | d_digit_span=0.04977373 | d_rep_span=-0.00002359
3.606 -> 3.608 | states 250 -> 250 | d_x_std=0.00007291 | d_digit_span=-0.07187873 | d_rep_span=0.00011389
3.608 -> 3.610 | states 250 -> 250 | d_x_std=0.00007400 | d_digit_span=0.06166452 | d_rep_span=0.00012557
------------------------------------------------------------------------
Done. Wrote outputs/logistic_map_regime_scan_deltas_v1.csv

Key rows from outputs/logistic_map_regime_scan_deltas_v1.csv

r_prev	r_curr	delta_unique_states	rel_delta_x_std	rel_delta_digit_sum_span_std	rel_delta_repetition_span_std

3.540	3.542	0	0.00075563	0.01210515	0.0
3.542	3.544	4	0.00155792	0.06528254	inf
3.544	3.546	0	0.00081556	0.03190231	0.31610738
3.546	3.548	0	0.00082486	0.02774720	0.14976269


Main result

Result A - transition amplification

At the critical transition:

3.542 -> 3.544

states: 4 -> 8


The relative change in x_std is only about:

0.00155792


But the relative change in digit_sum_span_std is:

0.06528254


This means the Omniabase transition signal is amplified by roughly a factor of 40 relative to the simple scalar statistic.

Result B - pre-transition sensitivity

Even before the visible state jump:

3.540 -> 3.542

states remain 4 -> 4


The relative change in x_std is:

0.00075563


But the relative change in digit_sum_span_std is already:

0.01210515


This suggests that Omniabase is not only amplifying the transition after it happens. It is also sensing pre-transition tension earlier than the standard scalar variance.

Result C - chaotic micro-structure

Inside the chaotic region, x_std increases only slowly and monotonically.

But the Omniabase delta signals continue to oscillate, including positive and negative swings.

This indicates that Omniabase is not merely tracking amplitude. It is reacting to internal representational micro-structure across bases.


---

Experiment 5 - Synthetic transition score v1

Purpose

A synthetic score was introduced to move from dispersed indicators to a single composite measure of structural transition pressure.

The goal was to test whether a unified Omniabase score could act as a practical detector of:

transition events

pre-transition tension

regime instability concentration


rather than requiring manual inspection of multiple raw metrics.

Run command

python experiments/build_transition_score_v1.py

Observed console output

------------------------------------------------------------------------
r=3.540 | states=4 | x_std=0.20914972 | digit_span=1.81231895 | rep_span=0.00000000 | score=0.011666
r=3.542 | states=4 | x_std=0.20930776 | digit_span=1.83425734 | rep_span=0.00000000 | score=0.046356
r=3.544 | states=8 | x_std=0.20963384 | digit_span=1.95400230 | rep_span=0.02682977 | score=0.347596
r=3.546 | states=8 | x_std=0.20980481 | digit_span=2.01633950 | rep_span=0.03531086 | score=0.311746
r=3.548 | states=8 | x_std=0.20997787 | digit_span=2.07228738 | rep_span=0.04060010 | score=0.313498
r=3.550 | states=8 | x_std=0.21015307 | digit_span=2.14927313 | rep_span=0.04060010 | score=0.264789
r=3.552 | states=8 | x_std=0.21033045 | digit_span=2.19730030 | rep_span=0.04060010 | score=0.222723
r=3.554 | states=8 | x_std=0.21051004 | digit_span=2.27211355 | rep_span=0.04060010 | score=0.244302
r=3.556 | states=8 | x_std=0.21069189 | digit_span=2.33304522 | rep_span=0.04060010 | score=0.226343
r=3.558 | states=8 | x_std=0.21087602 | digit_span=2.40870814 | rep_span=0.04060010 | score=0.241516
r=3.560 | states=8 | x_std=0.21106250 | digit_span=2.47853283 | rep_span=0.04060010 | score=0.228966
r=3.562 | states=8 | x_std=0.21125134 | digit_span=2.58069757 | rep_span=0.04060010 | score=0.265744
r=3.564 | states=8 | x_std=0.21144259 | digit_span=2.65922333 | rep_span=0.04060010 | score=0.231945
r=3.566 | states=16 | x_std=0.21153139 | digit_span=2.84650630 | rep_span=0.04944882 | score=0.457850
r=3.568 | states=243 | x_std=0.21155990 | digit_span=2.92055620 | rep_span=0.05284358 | score=0.370881
r=3.570 | states=250 | x_std=0.21160416 | digit_span=2.95155107 | rep_span=0.05293208 | score=0.323521
r=3.572 | states=250 | x_std=0.21163155 | digit_span=3.01691285 | rep_span=0.05364175 | score=0.354674
r=3.574 | states=250 | x_std=0.21165431 | digit_span=2.93297598 | rep_span=0.05193635 | score=0.252994
r=3.576 | states=250 | x_std=0.21168170 | digit_span=2.97305942 | rep_span=0.05187424 | score=0.312953
r=3.578 | states=250 | x_std=0.21172159 | digit_span=2.94635156 | rep_span=0.05139884 | score=0.245229
r=3.580 | states=250 | x_std=0.21176161 | digit_span=3.03157204 | rep_span=0.05141011 | score=0.372782
r=3.582 | states=250 | x_std=0.21180295 | digit_span=3.01168340 | rep_span=0.04996256 | score=0.260842
r=3.584 | states=250 | x_std=0.21184699 | digit_span=3.06421584 | rep_span=0.04961726 | score=0.325603
r=3.586 | states=250 | x_std=0.21189396 | digit_span=3.12579133 | rep_span=0.04892404 | score=0.340051
r=3.588 | states=250 | x_std=0.21194285 | digit_span=3.13632946 | rep_span=0.04899385 | score=0.298155
r=3.590 | states=250 | x_std=0.21199342 | digit_span=3.15523910 | rep_span=0.04953935 | score=0.314811
r=3.592 | states=250 | x_std=0.21204689 | digit_span=3.16104764 | rep_span=0.05141206 | score=0.315132
r=3.594 | states=250 | x_std=0.21210166 | digit_span=3.12071833 | rep_span=0.05151515 | score=0.254189
r=3.596 | states=250 | x_std=0.21216010 | digit_span=3.14652433 | rep_span=0.05151515 | score=0.314646
r=3.598 | states=250 | x_std=0.21221976 | digit_span=3.17646698 | rep_span=0.05151515 | score=0.324316
r=3.600 | states=250 | x_std=0.21228227 | digit_span=3.16634845 | rep_span=0.05191061 | score=0.288924
r=3.602 | states=250 | x_std=0.21234720 | digit_span=3.14923145 | rep_span=0.05193420 | score=0.283155
r=3.604 | states=250 | x_std=0.21241470 | digit_span=3.15838081 | rep_span=0.05193420 | score=0.309059
r=3.606 | states=250 | x_std=0.21248464 | digit_span=3.20815454 | rep_span=0.05191061 | score=0.366228
r=3.608 | states=250 | x_std=0.21255755 | digit_span=3.13627581 | rep_span=0.05202450 | score=0.207865
r=3.610 | states=250 | x_std=0.21263155 | digit_span=3.19794033 | rep_span=0.05215007 | score=0.380064
------------------------------------------------------------------------
mean_score=0.283995
max_score=0.457850
min_score=0.011666
Done. Wrote outputs/logistic_map_transition_score_v1.csv

Condensed score table

r	unique_states	x_std	digit_sum_span_std	repetition_span_std	transition_score_v1

3.540	4	0.20914972	1.81231895	0.00000000	0.011666
3.542	4	0.20930776	1.83425734	0.00000000	0.046356
3.544	8	0.20963384	1.95400230	0.02682977	0.347596
3.566	16	0.21153139	2.84650630	0.04944882	0.457850
3.568	243	0.21155990	2.92055620	0.05284358	0.370881
3.610	250	0.21263155	3.19794033	0.05215007	0.380064


Main result

The synthetic score works, but it has a specific character:

it is strong as a transition-event detector

it is not yet a clean state estimator


Result A - first transition marked sharply

The first period-doubling transition is strongly marked:

r = 3.542 -> score 0.046356

r = 3.544 -> score 0.347596


This is a large jump despite only a weak change in simple scalar variance.

Result B - strongest peak near explosion into chaos

The maximum score appears at:

r = 3.566

transition_score_v1 = 0.457850


This is exactly the region where the system leaves clearly periodic behavior and explodes toward chaotic occupancy.

Result C - pre-transition tension exists

Before the visible state jump:

r = 3.540 -> score 0.011666

r = 3.542 -> score 0.046356


This is already a large relative increase while unique_states remains unchanged.

So the score preserves the earlier result: Omniabase appears to detect pre-transition tension before obvious scalar summaries react strongly.

Result D - chaotic region keeps breathing

After the main transition, the score does not stay saturated. It oscillates roughly between 0.20 and 0.38.

This suggests the score is still reacting to internal structural modulation inside chaos, rather than collapsing into a flat chaos = maximum indicator.

Interpretation

At its current stage, transition_score_v1 should be interpreted as:

a detector of structural events and transition stress

not yet as:

a canonical scalar measure of regime identity

This distinction matters.

The score is already useful. But its current weighting gives strong influence to local relative jumps, so it is event-sensitive by construction.


---

Experiment 6 - Ordered window test inside chaos (r ~ 3.83)

Purpose

The next critical test was to determine whether the current Omniabase score detects only violent transition edges, or whether it can also detect ordered windows embedded inside chaos.

This is a stronger test.

If the score drops inside the period-3 window near r ~ 3.83, then the method is not merely reacting to explosion or discontinuity. It is reacting to latent structural order.

Run command

python experiments/window_scan_383_v1.py

Observed output

------------------------------------------------------------------------
r=3.820 | states=300 | x_std=0.250558 | digit_span_std=3.465064 | rep_span_std=0.063162 | score=0.297405
r=3.821 | states=300 | x_std=0.250772 | digit_span_std=3.568846 | rep_span_std=0.063162 | score=0.311746
r=3.822 | states=300 | x_std=0.250985 | digit_span_std=3.614784 | rep_span_std=0.063162 | score=0.306079
r=3.823 | states=300 | x_std=0.251199 | digit_span_std=3.585620 | rep_span_std=0.063162 | score=0.288599
r=3.824 | states=300 | x_std=0.251412 | digit_span_std=3.623074 | rep_span_std=0.063162 | score=0.297463
r=3.825 | states=300 | x_std=0.251626 | digit_span_std=3.655589 | rep_span_std=0.061730 | score=0.294943
r=3.826 | states=300 | x_std=0.251840 | digit_span_std=3.708810 | rep_span_std=0.064560 | score=0.320257
r=3.827 | states=300 | x_std=0.252053 | digit_span_std=3.750556 | rep_span_std=0.061730 | score=0.287118
r=3.828 | states=3 | x_std=0.246757 | digit_span_std=0.471405 | rep_span_std=0.012724 | score=0.057393
r=3.829 | states=3 | x_std=0.246869 | digit_span_std=0.000000 | rep_span_std=0.000000 | score=0.000000
r=3.830 | states=3 | x_std=0.246981 | digit_span_std=0.000000 | rep_span_std=0.000000 | score=0.264706
r=3.831 | states=3 | x_std=0.247093 | digit_span_std=0.000000 | rep_span_std=0.000000 | score=0.264706
r=3.832 | states=3 | x_std=0.247206 | digit_span_std=0.000000 | rep_span_std=0.000000 | score=0.264706
r=3.833 | states=3 | x_std=0.247318 | digit_span_std=0.000000 | rep_span_std=0.000000 | score=0.264706
r=3.834 | states=3 | x_std=0.247430 | digit_span_std=0.000000 | rep_span_std=0.000000 | score=0.264706
r=3.835 | states=3 | x_std=0.247543 | digit_span_std=0.471405 | rep_span_std=0.012724 | score=0.399580
r=3.836 | states=3 | x_std=0.247656 | digit_span_std=0.000000 | rep_span_std=0.000000 | score=0.000000
r=3.837 | states=3 | x_std=0.247768 | digit_span_std=0.471405 | rep_span_std=0.012724 | score=0.399580
r=3.838 | states=3 | x_std=0.247881 | digit_span_std=0.000000 | rep_span_std=0.000000 | score=0.000000
r=3.839 | states=3 | x_std=0.247994 | digit_span_std=0.471405 | rep_span_std=0.012724 | score=0.399580
r=3.840 | states=3 | x_std=0.248106 | digit_span_std=0.471405 | rep_span_std=0.012724 | score=0.301550
r=3.841 | states=6 | x_std=0.248674 | digit_span_std=0.516398 | rep_span_std=0.021025 | score=0.339678
r=3.842 | states=6 | x_std=0.248788 | digit_span_std=0.516398 | rep_span_std=0.023243 | score=0.316492
r=3.843 | states=6 | x_std=0.248903 | digit_span_std=0.516398 | rep_span_std=0.017724 | score=0.258953
r=3.844 | states=6 | x_std=0.249018 | digit_span_std=0.471405 | rep_span_std=0.021025 | score=0.286829
r=3.845 | states=12 | x_std=0.249427 | digit_span_std=0.887625 | rep_span_std=0.024446 | score=0.470530
r=3.846 | states=12 | x_std=0.249544 | digit_span_std=0.866025 | rep_span_std=0.029878 | score=0.331521
r=3.847 | states=24 | x_std=0.250000 | digit_span_std=1.040833 | rep_span_std=0.031977 | score=0.428459
r=3.848 | states=24 | x_std=0.250119 | digit_span_std=1.103026 | rep_span_std=0.032219 | score=0.339618
r=3.849 | states=48 | x_std=0.250550 | digit_span_std=1.354006 | rep_span_std=0.040441 | score=0.457814
r=3.850 | states=48 | x_std=0.250671 | digit_span_std=1.306000 | rep_span_std=0.038167 | score=0.307221
r=3.851 | states=300 | x_std=0.252063 | digit_span_std=2.234193 | rep_span_std=0.053158 | score=0.584102
r=3.852 | states=300 | x_std=0.252285 | digit_span_std=2.464670 | rep_span_std=0.054378 | score=0.395655
r=3.853 | states=300 | x_std=0.252507 | digit_span_std=2.433983 | rep_span_std=0.052061 | score=0.299105
r=3.854 | states=300 | x_std=0.252729 | digit_span_std=2.671302 | rep_span_std=0.052565 | score=0.375628
r=3.855 | states=300 | x_std=0.252951 | digit_span_std=2.607444 | rep_span_std=0.054170 | score=0.311746
r=3.856 | states=300 | x_std=0.253173 | digit_span_std=2.784411 | rep_span_std=0.054941 | score=0.371261
r=3.857 | states=300 | x_std=0.253396 | digit_span_std=2.675626 | rep_span_std=0.056087 | score=0.297441
r=3.858 | states=300 | x_std=0.253619 | digit_span_std=2.836561 | rep_span_std=0.052601 | score=0.336181
r=3.859 | states=300 | x_std=0.253841 | digit_span_std=2.969837 | rep_span_std=0.057302 | score=0.364413
r=3.860 | states=300 | x_std=0.254064 | digit_span_std=2.937740 | rep_span_std=0.056637 | score=0.304037
------------------------------------------------------------------------
Done. Wrote outputs/logistic_map_window_383_v1.csv

Key rows from outputs/logistic_map_window_383_v1.csv

r	unique_states	x_std	digit_sum_span_std	repetition_span_std	transition_score_v1

3.826	300	0.251840	3.708810	0.064560	0.320257
3.827	300	0.252053	3.750556	0.061730	0.287118
3.828	3	0.246757	0.471405	0.012724	0.057393
3.829	3	0.246869	0.000000	0.000000	0.000000
3.830	3	0.246981	0.000000	0.000000	0.264706
3.835	3	0.247543	0.471405	0.012724	0.399580
3.841	6	0.248674	0.516398	0.021025	0.339678
3.845	12	0.249427	0.887625	0.024446	0.470530
3.851	300	0.252063	2.234193	0.053158	0.584102


Main result

Result A - collapse inside the ordered window

As the system enters the period-3 window:

r = 3.827 -> score 0.287118

r = 3.828 -> score 0.057393

r = 3.829 -> score 0.000000


This is the strongest result so far.

It shows that the score can collapse sharply inside an ordered island embedded in a region otherwise associated with chaos.

Result B - order detection is stronger than raw scalar calm

Inside the period-3 window, x_std decreases, but not in a dramatic or fully decisive way.

By contrast, the Omniabase score and its component cross-base dispersions collapse much more strongly.

This suggests that the method is not merely tracking a mild reduction in variance. It is detecting a stronger reduction in cross-base structural tension.

Result C - internal tension inside the window

Inside the period-3 window, the score does not remain uniformly minimal across all values.

For example:

r = 3.829 -> score 0.000000

r = 3.830 -> score 0.264706

r = 3.835 -> score 0.399580


This suggests that the current score may also react to internal tension or distance from the center of the ordered window.

That is interesting, but it also means the score is still partly event-sensitive rather than being a perfectly flat order indicator.

Result D - re-escalation at the window boundary

As the system exits the ordered island and re-enters cascaded instability:

r = 3.845 -> score 0.470530

r = 3.851 -> score 0.584102


This is fully consistent with the interpretation of the score as a detector of structural transition stress.

Interpretation

This experiment strongly improves the status of the project.

Before this test, the method had evidence for:

periodic tracking

transition amplification

pre-transition sensitivity


Now it also has initial evidence for:

ordered-window detection inside chaos


This is a more difficult result than simple edge detection.

It suggests that Omniabase is not merely reacting to explosive regime changes. It is at least partially sensitive to latent order even when that order is embedded inside a broader chaotic region.


---

Experiment 7 - Separation of state-like order and event-like tension

Purpose

The next refinement step was to separate two functions that were still blended inside transition_score_v1:

1. order-like structure


2. event-like transition stress



This was necessary because the previous synthetic score was useful as an event detector, but still mixed:

latent regime order

transition edge intensity

local instability inside already-ordered zones


The goal of this experiment was to test whether Omniabase can generate two distinct coordinates:

order_score_v1

event_score_v1


rather than a single mixed signal.

Run command

python experiments/build_state_event_scores_v1.py

Observed console output

--------------------------------------------------------------------------------
r=3.540 | states=4 | order=0.941646 | event=0.113063
r=3.542 | states=4 | order=0.939832 | event=0.117144
r=3.544 | states=8 | order=0.916843 | event=0.364402
r=3.546 | states=8 | order=0.911689 | event=0.334460
r=3.548 | states=8 | order=0.907063 | event=0.337775
r=3.550 | states=8 | order=0.900700 | event=0.311746
r=3.552 | states=8 | order=0.896730 | event=0.288599
r=3.554 | states=8 | order=0.890545 | event=0.301550
r=3.556 | states=8 | order=0.885507 | event=0.291746
r=3.558 | states=8 | order=0.879252 | event=0.302324
r=3.560 | states=8 | order=0.873480 | event=0.297463
r=3.562 | states=8 | order=0.865034 | event=0.316492
r=3.564 | states=8 | order=0.858542 | event=0.302551
r=3.566 | states=16 | order=0.835165 | event=0.470530
r=3.568 | states=243 | order=0.454228 | event=0.428459
r=3.570 | states=250 | order=0.444265 | event=0.395655
r=3.572 | states=250 | order=0.438861 | event=0.418721
r=3.574 | states=250 | order=0.445805 | event=0.311746
r=3.576 | states=250 | order=0.442491 | event=0.371261
r=3.578 | states=250 | order=0.444701 | event=0.297441
r=3.580 | states=250 | order=0.437648 | event=0.402324
r=3.582 | states=250 | order=0.439292 | event=0.299105
r=3.584 | states=250 | order=0.434948 | event=0.364413
r=3.586 | states=250 | order=0.429871 | event=0.375628
r=3.588 | states=250 | order=0.428994 | event=0.336181
r=3.590 | states=250 | order=0.427431 | event=0.347596
r=3.592 | states=250 | order=0.426951 | event=0.341144
r=3.594 | states=250 | order=0.430286 | event=0.283155
r=3.596 | states=250 | order=0.428153 | event=0.339618
r=3.598 | states=250 | order=0.425677 | event=0.347530
r=3.600 | states=250 | order=0.426514 | event=0.311746
r=3.602 | states=250 | order=0.427929 | event=0.307221
r=3.604 | states=250 | order=0.427173 | event=0.320257
r=3.606 | states=250 | order=0.423062 | event=0.366228
r=3.608 | states=250 | order=0.429002 | event=0.222723
r=3.610 | states=250 | order=0.423903 | event=0.380064
--------------------------------------------------------------------------------
Done. Wrote outputs/logistic_map_state_event_scores_v1.csv

Key rows from outputs/logistic_map_state_event_scores_v1.csv

r	unique_states	x_std	digit_sum_span_std	repetition_span_std	order_score_v1	event_score_v1

3.540	4	0.209150	1.812319	0.000000	0.941646	0.113063
3.542	4	0.209308	1.834257	0.000000	0.939832	0.117144
3.544	8	0.209634	1.954002	0.026830	0.916843	0.364402
3.564	8	0.211443	2.659223	0.040600	0.858542	0.302551
3.566	16	0.211531	2.846506	0.049449	0.835165	0.470530
3.568	243	0.211560	2.920556	0.052844	0.454228	0.428459
3.610	250	0.212632	3.197940	0.052150	0.423903	0.380064


Main result

This separation is real.

Result A - order score behaves like a regime coordinate

In periodic regimes, order_score_v1 remains high:

r = 3.540 -> 0.941646

r = 3.542 -> 0.939832


As the system moves through bifurcation and toward chaos, order_score_v1 degrades gradually and then drops sharply:

r = 3.566 -> 0.835165

r = 3.568 -> 0.454228


This is a much cleaner state distinction than the mixed transition score alone.

Result B - event score peaks near structural changes

event_score_v1 remains relatively low in stable periodic zones:

r = 3.540 -> 0.113063

r = 3.542 -> 0.117144


It rises sharply at the first visible period-doubling:

r = 3.544 -> 0.364402


It reaches a strong local maximum near the transition into dense chaotic occupancy:

r = 3.566 -> 0.470530


This confirms that the event coordinate is capturing structural change more directly than the state coordinate.

Result C - order and event are no longer the same signal

The important outcome is not only that both scores move. It is that they move differently.

order_score_v1 tracks the degree of structural organization

event_score_v1 tracks the intensity of change or instability


This means the repository now has the first version of a genuine coordinate pair rather than a single blended detector.

Interpretation

This is the first point where the project starts to look less like a single metric and more like a small coordinate system.

The logistic map is no longer described only through:

raw state values

simple variance

periodicity count


It is now described through two Omniabase-derived axes:

order

event


This is a stronger result than transition detection alone.

Updated conclusion

At this stage, the project supports the following stronger statement:

Omniabase Coordinate Discovery can produce at least two partially distinct coordinates on the logistic map: one associated with structural order, and one associated with transition tension.

This remains early-stage.

But it is now fair to say that the method is beginning to map the system as a structured phase-space description, not just as a sequence of isolated indicators.


---

Current conclusion

The current prototype supports the following statements:

1. Omniabase signatures track periodic regime structure.


2. Omniabase signatures continue differentiating regimes after simple state counters saturate.


3. Omniabase signatures amplify transition boundaries more strongly than simple scalar statistics such as x_std.


4. Omniabase signatures show initial evidence of pre-transition sensitivity.


5. A synthetic Omniabase score can compress those effects into a practical event detector.


6. The score shows initial evidence of detecting ordered windows embedded inside chaos.


7. Omniabase can produce at least two partially distinct coordinates on the logistic map: one associated with structural order, and one associated with transition tension.



At this point, Omniabase Coordinate Discovery is no longer only a speculative idea.

It now has an initial empirical basis for the claim that:

multi-base observation can expose latent transition structure that standard single-representation summaries under-express.


---

Current status

periodic tracking: confirmed

chaotic regime differentiation: confirmed

transition amplification: confirmed

pre-transition sensitivity: initial evidence confirmed

synthetic event score: confirmed

ordered-window detection inside chaos: initial evidence confirmed

state/event coordinate separation: initial evidence confirmed



---

Next step

The next correct step is not to change the dynamical system yet.

The correct next step is to refine the signature family and separate more clearly:

state-like structure

event-like tension


At the moment, the first coordinate pair is promising, but still preliminary.

The immediate target is to improve the coordinate family on the logistic map until it can distinguish more cleanly between:

periodic state

chaotic state

transition edge

ordered island inside chaos


Only after that should the method be tested on a second dynamical system.

## Experiment 8 - State/Event coordinate test inside the period-3 window (`r ~ 3.83`)

### Purpose

The next decisive test was to check whether the separated coordinate pair:

- `order_score_v1`
- `event_score_v1`

also remains meaningful inside an ordered island embedded in chaos.

This is stronger than simple transition detection.

If the pair holds here, then Omniabase is not merely reacting to violent changes.
It is mapping both:

- the quality of the current state
- the intensity of local structural change

inside a more complex phase landscape.

### Run command

```bash
python experiments/build_window_383_state_event_scores_v1.py

Observed console output

------------------------------------------------------------------------------------
r=3.820 | states=300 | order=0.046342 | event=0.317584 | mixed=0.297405
r=3.821 | states=300 | order=0.036611 | event=0.341490 | mixed=0.311746
r=3.822 | states=300 | order=0.032304 | event=0.339233 | mixed=0.306079
r=3.823 | states=300 | order=0.035040 | event=0.320492 | mixed=0.288599
r=3.824 | states=300 | order=0.031526 | event=0.334460 | mixed=0.297463
r=3.825 | states=300 | order=0.033108 | event=0.324269 | mixed=0.294943
r=3.826 | states=300 | order=0.023479 | event=0.364402 | mixed=0.320257
r=3.827 | states=300 | order=0.024227 | event=0.337775 | mixed=0.287118
r=3.828 | states=3 | order=0.763420 | event=0.046356 | mixed=0.057393
r=3.829 | states=3 | order=0.814310 | event=0.011666 | mixed=0.000000
r=3.830 | states=3 | order=0.814310 | event=0.264706 | mixed=0.264706
r=3.831 | states=3 | order=0.814310 | event=0.264706 | mixed=0.264706
r=3.832 | states=3 | order=0.814310 | event=0.264706 | mixed=0.264706
r=3.833 | states=3 | order=0.814310 | event=0.264706 | mixed=0.264706
r=3.834 | states=3 | order=0.814310 | event=0.264706 | mixed=0.264706
r=3.835 | states=3 | order=0.763420 | event=0.399580 | mixed=0.399580
r=3.836 | states=3 | order=0.814310 | event=0.011666 | mixed=0.000000
r=3.837 | states=3 | order=0.763420 | event=0.399580 | mixed=0.399580
r=3.838 | states=3 | order=0.814310 | event=0.011666 | mixed=0.000000
r=3.839 | states=3 | order=0.763420 | event=0.399580 | mixed=0.399580
r=3.840 | states=3 | order=0.763420 | event=0.301550 | mixed=0.301550
r=3.841 | states=6 | order=0.749002 | event=0.339678 | mixed=0.339678
r=3.842 | states=6 | order=0.743285 | event=0.316492 | mixed=0.316492
r=3.843 | states=6 | order=0.757041 | event=0.258953 | mixed=0.258953
r=3.844 | states=6 | order=0.765620 | event=0.286829 | mixed=0.286829
r=3.845 | states=12 | order=0.705886 | event=0.470530 | mixed=0.470530
r=3.846 | states=12 | order=0.710787 | event=0.331521 | mixed=0.331521
r=3.847 | states=24 | order=0.671049 | event=0.428459 | mixed=0.428459
r=3.848 | states=24 | order=0.665313 | event=0.339618 | mixed=0.339618
r=3.849 | states=48 | order=0.615844 | event=0.457814 | mixed=0.457814
r=3.850 | states=48 | order=0.622501 | event=0.307221 | mixed=0.307221
r=3.851 | states=300 | order=0.231945 | event=0.584102 | mixed=0.584102
r=3.852 | states=300 | order=0.208477 | event=0.395655 | mixed=0.395655
r=3.853 | states=300 | order=0.217838 | event=0.299105 | mixed=0.299105
r=3.854 | states=300 | order=0.187283 | event=0.375628 | mixed=0.375628
r=3.855 | states=300 | order=0.197022 | event=0.311746 | mixed=0.311746
r=3.856 | states=300 | order=0.174677 | event=0.371261 | mixed=0.371261
r=3.857 | states=300 | order=0.187372 | event=0.297441 | mixed=0.297441
r=3.858 | states=300 | order=0.178224 | event=0.336181 | mixed=0.336181
r=3.859 | states=300 | order=0.151398 | event=0.364413 | mixed=0.364413
r=3.860 | states=300 | order=0.158043 | event=0.304037 | mixed=0.304037
------------------------------------------------------------------------------------
Done. Wrote outputs/logistic_map_window_383_state_event_scores_v1.csv

Key rows from outputs/logistic_map_window_383_state_event_scores_v1.csv

r	unique_states	x_std	digit_sum_span_std	repetition_span_std	order_score_v1	event_score_v1

3.827	300	0.252053	3.750556	0.061730	0.024227	0.337775
3.828	3	0.246757	0.471405	0.012724	0.763420	0.046356
3.829	3	0.246869	0.000000	0.000000	0.814310	0.011666
3.834	3	0.247430	0.000000	0.000000	0.814310	0.264706
3.840	3	0.248106	0.471405	0.012724	0.763420	0.301550
3.845	12	0.249427	0.887625	0.024446	0.705886	0.470530
3.851	300	0.252063	2.234193	0.053158	0.231945	0.584102


Main result

This is the strongest confirmation so far.

Result A - order score detects the ordered island

As the system enters the period-3 window:

r = 3.827 -> order_score_v1 = 0.024227

r = 3.828 -> order_score_v1 = 0.763420

r = 3.829 -> order_score_v1 = 0.814310


This is a sharp structural jump from chaotic disorder to local order.

Result B - event score drops inside the ordered center

At the same time:

r = 3.827 -> event_score_v1 = 0.337775

r = 3.828 -> event_score_v1 = 0.046356

r = 3.829 -> event_score_v1 = 0.011666


This confirms that the event coordinate is not merely large everywhere inside the chaotic region. It can collapse when the system settles into a local ordered island.

Result C - the two coordinates remain partially independent

Inside the window, the pair no longer behaves as a single mixed indicator.

For example:

r = 3.830 -> order_score_v1 = 0.814310, event_score_v1 = 0.264706


This means the system can preserve high local order while still showing some transition-related tension.

That is exactly the kind of separation the project needed.

Result D - event reappears at the window boundary

As the system leaves the period-3 island and enters the local period-doubling cascade:

r = 3.845 -> event_score_v1 = 0.470530


When it fully re-enters dense chaotic occupancy:

r = 3.851 -> event_score_v1 = 0.584102


At the same time, order_score_v1 falls again.

This is fully consistent with the interpretation of the pair:

order_score_v1 tracks the quality of structural organization

event_score_v1 tracks the intensity of structural change


Interpretation

This experiment shows that the coordinate pair is not limited to the simple transition strip near r = 3.54 - 3.61.

It also remains meaningful inside a harder case:

an ordered island embedded inside chaos


That is a much stronger result than simple transition detection.

Updated conclusion

At this stage, the project supports the following stronger statement:

Omniabase Coordinate Discovery can produce a preliminary coordinate family in which structural order and transition tension remain partially separable, even inside ordered islands embedded within chaotic regimes.

This is still early-stage and should remain stated carefully.

But it is now justified to say that the method is beginning to map the logistic system with a real two-axis structural description rather than with a single blended detector.


Sì. Prima si salva.

Ma con una correzione importante:

il test è buono, però la frase “robustezza dimostrata” è ancora troppo forte.
Perché in questo script gli score clean e noisy sono normalizzati separatamente per condizione. Quindi il confronto assoluto tra valori puliti e rumorosi va interpretato con cautela.

La formula vera è:

## Experiment 9 - Noise robustness test on the logistic-map coordinate family

### Purpose

The next stress test was to inject controlled stochastic noise into the logistic map and check whether the coordinate family still preserves the same qualitative distinctions between:

- periodic regime
- transition regime
- ordered island inside chaos
- chaotic regime

This matters because success on a perfectly clean deterministic system is not enough.
A useful coordinate family should retain at least part of its qualitative geometry under mild perturbation.

### Noise setting

Gaussian noise was added after each logistic-map update with:

- `noise_std = 0.0005`
- fixed random seed: `42`

### Run command

```bash
python experiments/logistic_map_noise_robustness_v1.py

Observed console output

----------------------------------------------------------------------------------------
clean | r=3.540 | states=4 | order=0.814310 | event=0.011666 | mixed=0.000000
clean | r=3.566 | states=54 | order=0.763420 | event=0.297441 | mixed=0.297441
clean | r=3.829 | states=3 | order=0.814310 | event=0.301550 | mixed=0.301550
clean | r=3.851 | states=300 | order=0.231945 | event=0.584102 | mixed=0.584102
----------------------------------------------------------------------------------------
noisy | r=3.540 | states=300 | order=0.811565 | event=0.038332 | mixed=0.038332
noisy | r=3.566 | states=300 | order=0.730302 | event=0.320478 | mixed=0.347963
noisy | r=3.829 | states=300 | order=0.735237 | event=0.297441 | mixed=0.297441
noisy | r=3.851 | states=300 | order=0.222712 | event=0.580036 | mixed=0.584102
----------------------------------------------------------------------------------------
Done. Wrote outputs/logistic_map_noise_robustness_v1.csv

Key rows from outputs/logistic_map_noise_robustness_v1.csv

condition	r	unique_states	x_std	order_score_v1	event_score_v1	transition_score_v1

clean	3.540	4	0.366432	0.814310	0.011666	0.000000
clean	3.566	54	0.370334	0.763420	0.297441	0.297441
clean	3.829	3	0.246869	0.814310	0.301550	0.301550
clean	3.851	300	0.252063	0.231945	0.584102	0.584102
noisy	3.540	300	0.366465	0.811565	0.038332	0.038332
noisy	3.566	300	0.370346	0.730302	0.320478	0.347963
noisy	3.829	300	0.246898	0.735237	0.297441	0.297441
noisy	3.851	300	0.252069	0.222712	0.580036	0.584102


Main result

The result is encouraging.

Result A - qualitative order separation survives mild noise

Under noise, unique_states becomes saturated because jitter makes nearly every sampled value distinct.

However, order_score_v1 still preserves a strong separation between:

ordered/structured regimes

chaotic regimes


For example, in the noisy condition:

r = 3.540 -> order_score_v1 = 0.811565

r = 3.829 -> order_score_v1 = 0.735237

r = 3.851 -> order_score_v1 = 0.222712


This suggests that the coordinate family is not relying only on raw uniqueness counts.

Result B - the chaotic regime still carries the strongest event load

In the noisy condition:

r = 3.851 -> event_score_v1 = 0.580036


This remains the strongest event value in the tested set, consistent with the idea that the coordinate family still recognizes the most unstable regime as the highest transition/tension zone.

Result C - the ordered island inside chaos remains partially distinguishable

Even under noise:

r = 3.829 retains much higher order than r = 3.851


This is important because it suggests that the ordered window is not completely erased by mild perturbation at the level of the Omniabase-derived coordinates.

Interpretation

This is not yet a proof of full robustness.

A technical caution is necessary:

the current scoring pipeline normalizes the clean and noisy conditions separately, so absolute cross-condition score comparison should be interpreted carefully.

What this experiment does support is a weaker but still important claim:

the qualitative geometry of the coordinate family appears to survive mild noise.

That is already useful.

Updated conclusion

At this stage, the project supports the following additional statement:

The preliminary order/event coordinate family shows initial qualitative robustness under mild stochastic perturbation on the logistic map.

This should still be treated as initial evidence, not as a final robustness claim.


---

## Experiment 10 - Weight sensitivity test for the order/event coordinate family

### Purpose

The next stress test was to check whether the emerging `order/event` geometry depends too strongly on one specific manual weighting choice.

The goal was not to prove exact numerical invariance.
The goal was to test **qualitative invariance**:

- ordered islands should remain high in `order_score`
- transition zones should remain high in `event_score`
- chaotic regions should remain low in `order_score` and relatively high in `event_score`

under several reasonable weight perturbations.

### Run command

```bash
python experiments/weight_sensitivity_v1.py

Observed console output

----------------------------------------------------------------------------------------
order_base + event_base
 r=3.827 | states=300 | order=0.024227 | event=0.337775
 r=3.829 | states=3 | order=0.814310 | event=0.011666
 r=3.845 | states=12 | order=0.705886 | event=0.470530
 r=3.851 | states=300 | order=0.231945 | event=0.584102
order_more_unique + event_more_delta
 r=3.827 | states=300 | order=0.013490 | event=0.395780
 r=3.829 | states=3 | order=0.803814 | event=0.027000
 r=3.845 | states=12 | order=0.695393 | event=0.551634
 r=3.851 | states=300 | order=0.211475 | event=0.588698
order_more_digit + event_more_static
 r=3.827 | states=300 | order=0.034963 | event=0.342417
 r=3.829 | states=3 | order=0.824806 | event=0.000000
 r=3.845 | states=12 | order=0.716380 | event=0.370591
 r=3.851 | states=300 | order=0.252414 | event=0.573966
order_more_rep + event_more_rep_delta
 r=3.827 | states=300 | order=0.038161 | event=0.375267
 r=3.829 | states=3 | order=0.772097 | event=0.015000
 r=3.845 | states=12 | order=0.663673 | event=0.528343
 r=3.851 | states=300 | order=0.224660 | event=0.613393
----------------------------------------------------------------------------------------
Done. Wrote outputs/logistic_map_weight_sensitivity_v1.csv

Key rows from outputs/logistic_map_weight_sensitivity_v1.csv

r	states	order_profile	event_profile	order_score	event_score

3.827	300	order_base	event_base	0.024227	0.337775
3.827	300	order_more_digit	event_more_static	0.034963	0.342417
3.829	3	order_base	event_base	0.814310	0.011666
3.829	3	order_more_rep	event_more_rep_delta	0.772097	0.015000
3.845	12	order_base	event_base	0.705886	0.470530
3.845	12	order_more_unique	event_more_delta	0.695393	0.551634
3.851	300	order_base	event_base	0.231945	0.584102
3.851	300	order_more_rep	event_more_rep_delta	0.224660	0.613393


Main result

The coordinate family is not fragile to reasonable weight perturbations.

Result A - ordered island remains strongly ordered

At r = 3.829, the period-3 window remains strongly high-order across all tested profiles:

0.814310

0.803814

0.824806

0.772097


This is far above the neighboring chaotic point at r = 3.827.

Result B - chaotic point remains low-order

At r = 3.827, the chaotic side remains strongly low-order across all tested profiles:

0.024227

0.013490

0.034963

0.038161


This preserves a large structural gap relative to the ordered island.

Result C - transition zone remains event-dominant

At r = 3.845, near the exit of the ordered window and onset of the local cascade, event_score remains high across all profiles:

0.470530

0.551634

0.370591

0.528343


So the event coordinate still identifies the transition boundary as an event-rich zone.

Result D - dense chaos remains the strongest event region

At r = 3.851, the fully chaotic regime remains the strongest event-loaded point in every tested profile:

0.584102

0.588698

0.573966

0.613393


This is strong evidence that the event axis is not a fragile artifact of one specific weighting.

Interpretation

This experiment does not prove universality.

But it does support a strong intermediate claim:

the qualitative order/event geometry is stable under reasonable weight perturbations.

That is enough to justify moving beyond the logistic map.

Updated conclusion

At this stage, the project supports the following stronger statement:

Omniabase Coordinate Discovery yields a preliminary coordinate family whose qualitative geometry remains stable under mild stochastic perturbation and under reasonable weight perturbations on the logistic map.

This is the minimum robustness threshold needed before testing a second dynamical system.



---

## Experiment 11 - Initial multibase scan on the 2D Hénon map

### Purpose

The first step beyond the logistic map was to test whether Omniabase signatures remain meaningful on a discrete two-dimensional dynamical system.

The Hénon map is the minimum serious extension beyond the 1D case:

- two-dimensional state
- discrete-time dynamics
- strange attractor regime under standard parameters

This makes it a useful test for whether multibase signatures are extracting structure from the attractor geometry rather than only from a scalar time series.

### System

Standard Hénon map:

- `a = 1.4`
- `b = 0.3`

Update rule:

- `x_(n+1) = 1 - a * x_n^2 + y_n`
- `y_(n+1) = b * x_n`

### Initial settings

- initial state: `x0 = 0.1`, `y0 = 0.1`
- total iterations: `1200`
- burn-in: `400`
- bases: `2` to `16`
- decimal precision per state: `12` digits

### Run command

```bash
python experiments/henon_multibase_v0.py

Observed console output

------------------------------------------------------------------------
steps_written=800
x_digit_sum_span_std=2.417243
x_repetition_span_std=0.061453
y_digit_sum_span_std=2.409388
y_repetition_span_std=0.061799
------------------------------------------------------------------------
Done. Wrote outputs/henon_multibase_v0.csv

Sample rows from outputs/henon_multibase_v0.csv

step	x	y	x_scaled	y_scaled	x_digit_sum_span	x_repetition_span	y_digit_sum_span	y_repetition_span	xy_digit_sum_span_mean	xy_repetition_span_mean

0	-0.370335	0.354145	0.353457	0.852431	51.0	0.090909	60.0	0.181818	55.5	0.136364
1	1.162235	-0.111100	0.941324	0.301280	50.0	0.181818	57.0	0.181818	53.5	0.181818
2	-1.002237	0.348671	0.111100	0.845950	54.0	0.090909	49.0	0.090909	51.5	0.090909
3	-0.057396	-0.300671	0.473507	0.076822	53.0	0.090909	50.0	0.090909	51.5	0.090909
4	0.694770	-0.017219	0.761928	0.412431	55.0	0.090909	49.0	0.181818	52.0	0.136364
5	0.307525	0.208431	0.613374	0.679599	56.0	0.181818	48.0	0.090909	52.0	0.136364
6	0.875953	0.092258	0.831435	0.542055	50.0	0.181818	51.0	0.090909	50.5	0.136364
7	-0.170668	0.262786	0.430049	0.743953	53.0	0.090909	49.0	0.090909	51.0	0.090909
8	1.222049	-0.051200	0.964270	0.372198	45.0	0.090909	55.0	0.090909	50.0	0.090909
9	-1.140884	0.366615	0.057913	0.867195	58.0	0.272727	51.0	0.090909	54.5	0.181818


Main result

The first 2D scan is successful.

Result A - multibase signal remains active in 2D

The signature dispersions remain clearly nontrivial across the attractor:

x_digit_sum_span_std = 2.417243

y_digit_sum_span_std = 2.409388

x_repetition_span_std = 0.061453

y_repetition_span_std = 0.061799


So the method does not collapse when moving from 1D to 2D.

Result B - x and y show strong structural symmetry

The x and y span statistics are extremely close.

This is consistent with the Hénon structure, since y_(n+1) is directly derived from x_n.

That suggests the multibase complexity of one component is structurally reflected in the other.

Result C - no ordered-collapse signature appears in the standard strange-attractor regime

The observed span means remain active and distributed. There is no collapse toward near-zero signatures of the kind seen in periodic windows of the logistic map.

This is consistent with the fact that the standard Hénon parameters lie in a strange-attractor regime rather than a simple periodic one.

Interpretation

This first 2D experiment does not yet answer how Omniabase should represent multidimensional state.

But it establishes an important starting point:

multibase signatures remain meaningful in a two-dimensional discrete system.

The next architectural question is therefore not whether the method survives 2D.

It is:

how should 2D state be represented most usefully for Omniabase?

At this point two layers are justified:

1. component-wise signatures (x, y)


2. simple joint-derived signatures from the full state





---

Author

Massimiliano Brighindi