# T=2 round-4 model deployment

The production ROM now links the 1,011,355-parameter T=2 round-4 actor whose
host-C Kakuna benchmark scored 30.49%. The importer pins export SHA256
`847189ef2659c07b6efc98920a9b7084319997760ffdbfd16e19e667b7f86cd7`.
Legal argmax, FP32 recurrent state, lookup-table nonlinearities and the existing
public observation adapter remain the production inference path.

ROM SHA256:
`38cd802905abb9bea88411ed35c15abb5daedfb9dedf755bd64977b73dfe3321`.

The rebuilt ROM passed all existing mGBA integration checks: five-turn smoke,
nine privacy cases, two complete trainer battles with audio and recurrent reset,
and the Rustboro gym battle. No runtime faults occurred. The verifier reproduced
1,530/1,531 legal argmax agreement across 32 held-out episodes; maximum
logit/hidden errors were 0.02557/0.01534 within the existing gates. All 13
importer/heap tests passed.

Eight-decision mGBA kernel timing measured median 2.716 seconds for Thumb and
2.368 seconds for ARM/IWRAM. Host fixture logits, hidden state and actions
matched both GBA builds. Production trainer battles averaged 3.812 seconds per
decision, including frame scheduling. These are emulator measurements; the
30.49% Kakuna result remains the separate host-C Showdown benchmark.

The ROM has 5,248,592 bytes free within 32 MiB. The linked weight payload was
checked byte-for-byte against the import. Prior weights and ROM artifacts were
backed up before replacement.

Pinned ROM, ELF/map, logs, verifier fixtures, timing results, privacy results,
battle evidence and `deployment.json`:
`/home/eddie/metamon/models/plastic-ox-t2-r4-deployment-20261007`.
The research protocol is documented in
`/home/eddie/repos/metamon/docs/kakuna_capacity_coverage_20261007.md`.
